/**
 * Get any variable for current attribute of HTML tag.
 * If there are more than 1 tag, the value from first tag will be returned.
 * @param {string} path - Element selector by define id or class etc.
 * @param {string} attr - Attribute selected to return value.
 * @return {string} - the value of attribute for selected path.
 * */
function getVariable(path, attr) {
  return $(path).attr(attr);
}

/**
 *  Get directions from Google Directions API by calling to backend.
 *  @param {array.<string>} placesList - list contains place_id for each place.
 *  @return {object} - direction information for places list
 *  */
function getDirectionTime(placesList) {
  let response = {responseJSON: undefined};
  response = $.ajax({
    type: 'POST',
    url: getVariable('#script', 'directions_url'),
    async: false,
    data: {
      csrfmiddlewaretoken: getVariable('#script', 'token'),
      places: JSON.stringify(placesList),
    },
  });
  return response.responseJSON;
}

/** Change cloud sync icon to display syncing */
function displaySyncing() {
  document.getElementById('cloud-connect').innerText = 'cloud_sync';
}

/** Listen on planner title change */
// queue for detect changing
const NAME_CHANGE_QUEUE = [];
// planner title element in HTML
let LATEST_NAME = document.getElementById('place_name').innerText;
document.getElementById('place_name').addEventListener('input', function(e) {
  displaySyncing();
  /* Push event to queue to check if there's still editing. */
  NAME_CHANGE_QUEUE.push(e);
  setTimeout(function() {
    NAME_CHANGE_QUEUE.pop(); // Remove event from queue after delayed
    displaySyncing();
    const name = document.getElementById('place_name').innerText;
    if (NAME_CHANGE_QUEUE.length === 0 && LATEST_NAME !== name) {
      // If the edit is stopped and there's a change.
      sendEdit('name', name);
      LATEST_NAME = name;
      // change page title to current title.
      document.title = name + ' | ThaiRepose';
    } else if (NAME_CHANGE_QUEUE.length === 0 && LATEST_NAME === name) {
      // If there's no change.
      document.getElementById('cloud-connect').innerText = 'cloud_done';
    }
  }, 2000); // delay for 2 seconds after any change.
});

const MAX_PLACES_PER_LIST = 25;

/**
 * Collect all places in this page.
 * Split into maximum 25 places per array.
 * Send places to `getDirectionTime()` each array to get directions.
 */
async function getTravelTime() {
  const places = $('tr[name="place"]').toArray();
  const placesIdList = {};
  for (let idx = 0; idx < places.length; idx++) {
    const requestRound = Math.floor(idx / MAX_PLACES_PER_LIST);
    if (idx % MAX_PLACES_PER_LIST === 0) {
      // Initialize array
      placesIdList[requestRound] = [places[idx].id];
    } else {
      // Push value to initialized array.
      placesIdList[requestRound].push(places[idx].id);
    }
  }
  /* Return if there's only 1 place. */
  if (placesIdList.length <= 1) {
    return;
  }
  for (const requestRound in placesIdList) {
    /* Filter the existed properties */
    if (placesIdList.hasOwnProperty(requestRound)) {
      /* Get directions from server */
      const requestedDirection = getDirectionTime(placesIdList[requestRound]);
      /* add directions information to global variable. */
      directions = Object.assign({[requestRound]: requestedDirection});
      /* Display the received direction to display time schedule. */
      await displayTravelTime(requestedDirection);
    }
  }
}

/**
 * Display time schedule received from `displayTimeTravel()`
 * and calculated in the table.
 * @param {object} directions - Object contains information about directions.
 * @param {array.<object>} directions.geocoded_waypoints - PlaceId list
 * requested for directions.
 * @param {array.<object>} directions.routes - Routes from previous place
 * to next place, respectively.
 * @param {array.<object>} directions.routes.legs - Steps for each route
 * from previous place to next place, contains duration in seconds.
 */
function displayTime(directions) {
  if (directions === undefined) {
    return;
  }
  let placeOccurredStart = {};
  let placeOccurredStop = {};
  for (let i = 1; i < directions.geocoded_waypoints.length; i++) {
    let startIdx = 0;
    let stopIdx = 0;
    if (directions.geocoded_waypoints[i - 1].place_id in placeOccurredStart) {
      startIdx = placeOccurredStart[directions.geocoded_waypoints[i - 1].place_id];
      placeOccurredStart[directions.geocoded_waypoints[i - 1].place_id] += 1;
    } else {
      placeOccurredStart[directions.geocoded_waypoints[i - 1].place_id] = 1;
    }
    if (directions.geocoded_waypoints[i].place_id in placeOccurredStop) {
      stopIdx = placeOccurredStop[directions.geocoded_waypoints[i].place_id];
      placeOccurredStop[directions.geocoded_waypoints[i].place_id] += 1;
    } else {
      placeOccurredStop[directions.geocoded_waypoints[i].place_id] = 1;
    }
    const start = directions.geocoded_waypoints[i - 1].place_id;
    const stop = directions.geocoded_waypoints[i].place_id;
    // Compute second to be divided by 1 minute.
    let directionTime = (directions.routes[0].legs[i - 1].duration.value) / 60;
    directionTime = Math.ceil(directionTime) * 60;
    console.log(startIdx);
    const departure = document.getElementsByName('departure-' + start)[startIdx];
    console.log(departure);
    let nextPlace = $(departure).parent().parent().next().children()[stopIdx];
    let nextDay = false;
    if (nextPlace === undefined) {
      nextPlace = $(departure).parents('[name=\'day-table\']').next().next()
          .find(`td[name='arrival-${stop}']`)[0];
      nextDay = true;
    }
    const arrival = document.getElementsByName('arrival-' + stop)[stopIdx];
    if (nextPlace !== arrival) {
      continue;
    }
    const time = createTime(departure.value);
    time.setTime(time.getTime() + (directionTime * 1000));
    if (nextDay && time.getDate() === 1) {
      continue;
    }
    arrival.setAttribute('value', time.toString());
    arrival.innerText = getTimeFormat(time);
    const nextDeparture = document.getElementsByName('departure-' + stop)[stopIdx];
    nextDeparture.min = getTimeFormat(time);
    if (createTime(nextDeparture.value) < time) {
      let departureDay = $(departure).parents("div[name='day-table']").index();
      let nextDepartureDay = $(nextDeparture).parents("div[name='day-table']").index();
      if (nextDepartureDay > departureDay) {
        continue;  // Continue if day isn't the same.
      }
      nextDeparture.value = getTimeFormat(time);
    }
  }
}

/**
 * Synchronous function to display time and store time in database.
 * @param {object} directions - Object contains information about directions.
 */
async function displayTravelTime(directions) {
  await displayTime(directions);
  await checkOverDate();
  displaySyncing();
  await updatePlacesInDatabase();
}

const MAXIMUM_PLACES_PER_DAY = 10;

/**
 * Get amount of places in specified day.
 * @param {number} dayNumber - The day number that wants to check.
 * @return {number} - Amount of places in that day.
 */
function amountPlacesInDay(dayNumber) {
  const tableId = 'table-day-' + dayNumber;
  const table = document.getElementById(tableId);
  return table.tBodies[0].rows.length;
}

/**
 * Create a table for each day.
 * @param {number} dayNumber - The day number of the trip.
 */
function tableCreate(dayNumber) {
  // select part to display the table
  const body = document.getElementById('trip-days');
  // create day name container
  const titleDiv = document.createElement('div');
  const titleText = document.createElement('h1');

  // settings in day name container
  titleDiv.id = 'day-title';
  titleDiv.classList.add('mt-10', 'mx-8');
  titleText.classList.add('text-2xl');
  titleText.innerHTML = 'Day ' + dayNumber;
  body.appendChild(titleDiv);
  titleDiv.appendChild(titleText);

  // settings in day table container
  const tableDiv = document.createElement('div');
  const tbl = document.createElement('table');
  tableDiv.id = dayNumber;
  tableDiv.setAttribute('name', 'day-table');
  tableDiv.classList.add('w-full', 'md:px-8');
  tbl.classList.add('w-full', 'text-gray-400', 'text-sm');
  tbl.id = 'table-day-' + dayNumber;
  const thead = tbl.createTHead();
  const tbody = tbl.createTBody();
  const tr = thead.insertRow();
  thead.classList.add('bg-translucent', 'text-gray-700', 'shadow-lg');
  tbody.classList.add('text-gray-700');
  tr.insertCell().outerHTML = '<th class=\'py-3 text-center\'>Arrival</th>';
  tr.insertCell().outerHTML = '<th class=\'py-3 text-center\'>Place</th>';
  tr.insertCell().outerHTML = '<th class=\'py-3 text-center\'>Departure</th>';
  tr.insertCell().outerHTML = '<th class=\'py-3 text-center\'>Action</th>';
  body.appendChild(tableDiv);
  tableDiv.appendChild(tbl);
}

/**
 * Add place to the table and send changes to database.
 * @param {number} dayNumber - Day number to add place.
 * @param {string} placeName - Place name to be displayed.
 * @param {string} placeVicinity - Place address to be displayed.
 * @param {string} placeId - Place id to be calculated direction time.
 * @param {string} arrival - Arrival for this place in string
 * to be displayed and calculated.
 * @param {string} departure - Departure for this place in string
 * to be displayed and calculated.
 */
function addPlace(dayNumber, placeName, placeVicinity,
    placeId, arrival = '', departure = '00:00') {
  addPlaceToTable(dayNumber, placeName, placeVicinity, placeId,
      arrival, departure);
  addPlaceToDatabase(dayNumber, placeName, placeVicinity, placeId,
      arrival, departure);
}

/**
 * Add place to a table in specified day from `AddPlace()`.
 * @param {number} dayNumber - Day number to add this place.
 * @param {string} placeName - Place name to be displayed.
 * @param {string} placeVicinity - Place address to be displayed.
 * @param {string} placeId - Place id to be calculated direction time.
 * @param {string} arrival - Arrival for this place in string
 * to be displayed and calculated.
 * @param {string} departure - Departure for this place in string
 * to be displayed and calculated.
 */
function addPlaceToTable(dayNumber, placeName, placeVicinity,
    placeId, arrival, departure) {
  const tableId = 'table-day-' + dayNumber;
  const table = document.getElementById(tableId);
  if (amountPlacesInDay(dayNumber) >= MAXIMUM_PLACES_PER_DAY) {
    alert('You\'ve reached maximum places for Day ' + dayNumber +
      '. Please add to another day or delete some place in Day ' +
      dayNumber + '.');
    return;
  }

  // Rows for each place in table body.
  const row = table.getElementsByTagName('tbody')[0].insertRow();
  row.setAttribute('name', 'place');
  row.id = placeId;
  const cell1 = row.insertCell(0);
  const cell2 = row.insertCell(1);
  const cell3 = row.insertCell(2);
  const cell4 = row.insertCell(3);

  // Arrival column
  cell1.setAttribute('name', 'arrival-' + (placeId));
  const time = createTime(arrival);
  cell1.setAttribute('value', time);
  cell1.innerText = arrival;
  cell1.id = 'time';
  cell1.classList.add('py-3', 'text-center', 'text-xl');

  // Place column.
  const div = document.createElement('div');
  const childDiv = document.createElement('div');
  const nameDiv = document.createElement('div');
  const descDiv = document.createElement('div');
  div.classList.add('flex', 'align-items-center');
  div.onclick = function() {
    window.open('/place/' + placeId + '/', '_blank');
  };
  div.style.cursor = 'pointer';
  childDiv.classList.add('ml-3');
  nameDiv.style.width = '25vw';
  nameDiv.innerHTML = `<span class="limit-text">${placeName}</span>`;
  childDiv.appendChild(nameDiv);
  descDiv.classList.add('text-gray-500');
  descDiv.style.width = '25vw';
  descDiv.innerHTML = `<span class="limit-text">${placeVicinity}</span>`;
  childDiv.appendChild(descDiv);
  div.appendChild(childDiv);
  cell2.appendChild(div);
  cell2.classList.add('p-3');

  // Departure column
  cell3.classList.add('p-3', 'text-center');
  cell3.innerHTML = `<input
    class="rounded-lg bg-translucent rounded-lg shadow-xl border-gray-200"
    type="time"
    id="time"
    name="departure-${placeId}"
    value="${departure}" 
    required />`;
  cell3.children[0].addEventListener('change', timeChanged);

  // Actions column
  cell4.classList.add('p-3', 'text-center');
  cell4.innerHTML = `<button 
    class="text-gray-700 hover:text-black lg:mx-1 
        focus:outline-none hover:scale-150"
    onclick="moveUp(this)">
      <span class="material-icons material-icons-outlined md-18">
        north
      </span>
    </button>
    <button 
    class="text-gray-700 hover:text-black lg:mx-1 
        focus:outline-none hover:scale-150" 
    onclick="moveDown(this)">
      <span class="material-icons material-icons-outlined md-18">
        south
      </span>
    </button>
    <button 
    class="text-gray-700 hover:text-red-600 lg:mx-1 
        focus:outline-none hover:scale-150" 
    onclick="delPlace(this)">
      <span class="material-icons material-icons-outlined md-18">
        delete_outline
      </span>
    </button>`;
}

/**
 * Add places to the database.
 * @param {number} dayNumber - Day number to be added.
 * @param {string} placeName - Place name to be added.
 * @param {string} placeVicinity - Place address be added.
 * @param {string} placeId - Place id to be added.
 * @param {string} arrival - Arrival for this place in string
 * to be added.
 * @param {string} departure - Departure for this place in string
 * to be added.
 */
function addPlaceToDatabase(dayNumber, placeName, placeVicinity,
    placeId, arrival, departure) {
  displaySyncing();
  const place = {
    day: dayNumber,
    sequence: -1,
    place_id: placeId,
    place_name: placeName,
    place_vicinity: placeVicinity,
    arrival_time: arrival,
    departure_time: departure,
  };
  displaySyncing();
  sendEdit('addPlace', JSON.stringify(place));
}

/**
 * Delete a place in the Planner.
 * @param {object} obj - HTML object from where is it clicked.
 */
async function delPlace(obj) {
  displaySyncing();
  // Get sequence in the day for this place.
  const currRow = $(obj).parent().parent();
  // Get day for this place.
  const currDay = currRow.parentsUntil('div[name=\'day-table\']')
      .parent()[0].id;
  const data = {
    sequence: parseInt(currRow.index()) + 1,
    day: parseInt(currDay),
    place_id: currRow[0].id,
  };
  currRow.remove();
  displaySyncing();
  sendEdit('delPlace', JSON.stringify(data));
  await changeDirectionsTime();
}

/**
 * Trigger `moveItemUp()` to move place up to previous place.
 * @param {object} obj - HTML object from where it is clicked.
 */
async function moveUp(obj) {
  const day = Math.ceil($(obj).parents('div[name=\'day-table\']').index() / 2);
  const response = await moveItemUp(obj);
  if (response.status === 'OK') {
    response.day = day;
    displaySyncing();
    await sendEdit('moveUp', JSON.stringify(response));
    await changeDirectionsTime();
  }
}

/**
 * Move place up to previous sequence.
 * @param {object} obj - HTML object from where it is clicked.
 * @return {object} - Response after moving a place to update the database.
 */
function moveItemUp(obj) {
  const row = $(obj).parents('tr');
  const originSequence = row.index() + 1;
  if (row.index() === 0) {
    // If place is the first place of the day.
    let prevTable = $(obj).parents('table').parents('div').prev().prev();
    let prevTablePlaces = prevTable.children().children()
        .closest('tbody').children();
    // Check that previous table does not reach limit
    while (prevTablePlaces.length >= MAXIMUM_PLACES_PER_DAY) {
      if (prevTable[0].id === '1') {
        alert('All above days have reached maximum places. ' +
          'Please move to another day or delete some place ' +
          'in any above table.');
        return {status: 'Error'};
      }
      prevTable = prevTable.prev().prev();
      prevTablePlaces = prevTable.children().children()
          .closest('tbody').children();
      if (prevTablePlaces.length < MAXIMUM_PLACES_PER_DAY) {
        alert('Some days have reached maximum places. ' +
          'This place will be moved to Day ' + prevTable[0].id);
      }
    }
    if (prevTable.attr('name') !== 'day-table') {
      return {status: 'Error'};
    }
    if (prevTablePlaces.length === 0) {
      // insert place into above table as a first place
      const prevBody = prevTable.children().children()
          .closest('tbody');
      prevBody.prepend(row);
    } else {
      row.insertAfter(prevTablePlaces.last());
    }
    return {
      status: 'OK',
      day_moved: true,
      day_destination: Math.ceil(prevTable.index() / 2),
      sequence: originSequence,
    };
  }
  row.insertBefore(row.prev());
  return {status: 'OK', sequence: originSequence, day_moved: false};
}

/**
 * Trigger `moveItemDown()` to move place down to next place.
 * @param {object} obj - HTML object from where it is clicked.
 */
async function moveDown(obj) {
  const day = Math.ceil($(obj).parents('div[name=\'day-table\']').index() / 2);
  const response = await moveItemDown(obj);
  if (response.status === 'OK') {
    response.day = day;
    displaySyncing();
    await sendEdit('moveDown', JSON.stringify(response));
    await changeDirectionsTime();
  }
}

/**
 * Move place down to next sequence.
 * @param {object} obj - HTML object from where it is clicked.
 * @return {object} - Response after moving a place to update the database.
 */
function moveItemDown(obj) {
  const row = $(obj).parents('tr');
  const originSequence = row.index() + 1;
  const thisBody = $(obj).closest('tbody');
  const totalPlace = thisBody.children().length;
  if (row.index() === totalPlace - 1) {
    // Move to below table
    let nextTable = $(obj).parents('table').parents('div').next().next();
    let nextTablePlaces = nextTable.children().children()
        .closest('tbody').children();
    const totalDays = $('#days-selector')[0].value;
    // Check that next table does not reach limit
    while (nextTablePlaces.length >= MAXIMUM_PLACES_PER_DAY) {
      if (nextTable[0].id === totalDays) {
        alert('All below days have reached maximum places. ' +
          'Please move to another day or delete some place ' +
          'in any below table.');
        return {status: 'Error'};
      }
      nextTable = nextTable.next().next();
      nextTablePlaces = nextTable.children().children()
          .closest('tbody').children();
      if (nextTablePlaces.length < MAXIMUM_PLACES_PER_DAY) {
        alert('Some days have reached maximum places. ' +
          'This place will be moved to Day ' + nextTable[0].id);
      }
    }
    if (nextTable.attr('name') !== 'day-table') {
      return {status: 'Error'};
    }
    if (nextTablePlaces.length === 0) {
      // insert into next day as a first place
      const nextBody = nextTable.children().children()
          .closest('tbody');
      nextBody.prepend(row);
    } else {
      row.insertBefore(nextTablePlaces[0]);
    }
    return {
      status: 'OK',
      day_moved: true,
      day_destination: Math.ceil(nextTable.index() / 2),
      sequence: originSequence,
    };
  }
  row.insertAfter(row.next());
  return {status: 'OK', sequence: originSequence, day_moved: false};
}

const MAXIMUM_DAYS = 6;
/**
 * Add new day in the planner and add option for adding a new place.
 * @param {number} dayNumber - Specified number for that day.
 */
const addNewDay = function(dayNumber) {
  for (let i = 1; i <= dayNumber && i <= MAXIMUM_DAYS; i++) {
    const tableExist = $('#table-day-' + i).length > 0;
    if (tableExist) {
      continue;
    }
    // Create new table
    tableCreate(i);
    // Add option in add place
    addDayPlaceOption(i);
  }
};

/**
 * Remove a day from planner and remove options for adding a new place.
 * @param {number} dayNumber - Specified number for that day.
 */
const removeDay = function(dayNumber) {
  for (let i = MAXIMUM_DAYS; i >= dayNumber; i--) {
    // Remove table and day title
    const obj = $(`div[name="day-table"][id=${i}]`);
    const objTitle = obj.prev();
    obj.remove();
    objTitle.remove();
    // Remove option in add place
    removeDayPlaceOption(i);
  }
};

/**
 * Add option for adding a new place.
 * @param {number} dayNumber - Specified number for that day.
 */
function addDayPlaceOption(dayNumber) {
  const option = $('[name="add-place_day-selector"]');
  option.append($('<option>', {
    value: dayNumber,
    text: 'Day ' + dayNumber,
  }));
}

/**
 * Remove option for add new place section.
 * @param {number} dayNumber - Specified number for that day.
 */
function removeDayPlaceOption(dayNumber) {
  $(`[name="add-place_day-selector"] option[value="${dayNumber}"]`).remove();
}

/**
 * Initialize google map autocomplete for adding a new place.
 */
function initialize() {
  const input = document.getElementById('place-search');
  new google.maps.places.Autocomplete(input);
}

/**
 * Set timeout in milliseconds.
 * @param {Number} ms - time to delay in milliseconds.
 * @return {Promise<setTimeout>} - setTimeout function for specified seconds.
 */
function timeout(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// queue for detecting changing.
const CHANGING_QUEUE = [];
/**
 * Auto trigger after changed any departure time.
 * @param {object} event - The event of trigger.
 */
async function timeChanged(event) {
  if (CHANGING_QUEUE.length > 0) {
    return;
  }
  CHANGING_QUEUE.push(event);
  await timeout(3000);
  const arrival = $(event.target).parent().prev().prev();
  const departure = event.target;
  const departureTime = createTime(departure.value);
  const arrivalTime = createTime(arrival.text());
  if (arrivalTime > departureTime) {
    departure.value = getTimeFormat(arrivalTime);
  }
  await changeDirectionsTime();
  CHANGING_QUEUE.pop();
}

/**
 * Change all arrival time in Planner.
 */
async function changeDirectionsTime() {
  // Set all arrivals to blank.
  $.each($('[name^="arrival-"]'), function(index, obj) {
    obj.innerText = '';
  });
  // Get new directions if there's no information.
  if (directions === undefined) {
    await getTravelTime();
  }
  // Get all arrivals.
  for (const i in directions) {
    if (directions.hasOwnProperty(i)) {
      await displayTravelTime(directions[i]);
    }
  }
}

/**
 * Update places schedule in the database.
 */
function updatePlacesInDatabase() {
  const places = [];
  $.each($('tr[name="place"]'), function(index, obj) {
    const arrival = $(obj).find('[name^="arrival"]')[0].innerText;
    const departure = $(obj).find('[name^="departure"]')[0].value;
    const placeId = obj.id;
    const placeDay = Math.ceil($(obj)
        .parents('[name=\'day-table\']').index() / 2);
    const placeSequence = index + 1;
    places.push({
      place_id: placeId,
      day: placeDay,
      sequence: placeSequence,
      arrival: arrival,
      departure: departure,
    });
  });
  displaySyncing();
  sendEdit('changeTime', JSON.stringify(places));
}

const DAY_CHANGE_QUEUE = [];
let LATEST_DAY = document.getElementById('days-selector').value;

/**
 * Update day for the trip in database.
 * @param {number} days - days amount for this trip.
 */
async function updateDaysInDatabase(days) {
  displaySyncing();
  DAY_CHANGE_QUEUE.push(days);
  await timeout(750); // Delay for 750 ms before send changes to database.
  DAY_CHANGE_QUEUE.pop();
  displaySyncing();
  if (DAY_CHANGE_QUEUE.length === 0 && LATEST_DAY !== days) {
    displaySyncing();
    sendEdit('days', days);
    LATEST_DAY = days;
  } else if (DAY_CHANGE_QUEUE.length === 0 && LATEST_DAY === days) {
    document.getElementById('cloud-connect').innerText = 'cloud_done';
  }
}

/**
 * Decrease day for this planner.
 * @param {object} e - object of decrement button.
 */
function decrement(e) {
  const btn = e.target.parentNode.parentElement.querySelector(
      'button[data-action="decrement"]',
  );
  const target = btn.nextElementSibling;
  let value = Number(target.value);
  if (value > 1) {
    removeDay(value);
    value--;
  }
  target.value = value;
  updateDaysInDatabase(value);
}

/**
 * Increase day for this planner.
 * @param {object} e - object of increment button.
 */
function increment(e) {
  const btn = e.target.parentNode.parentElement.querySelector(
      'button[data-action="decrement"]',
  );
  const target = btn.nextElementSibling;
  let value = Number(target.value);
  if (value < 6) {
    value++;
    addNewDay(value);
  }
  target.value = value;
  updateDaysInDatabase(value);
}

/**
 * Bind decrement/increment button to function.
 */
$('button[data-action="decrement"]').bind('click', decrement);
$('button[data-action="increment"]').bind('click', increment);

/**
 * Detect changes in days box.
 */
document.getElementById('days-selector').addEventListener(
    'change',
    /**
           * Detect restricted maximum days in each planner.
           * @param {object} e - Object of days setting,
           */
    function(e) {
      if (e.target.value < 1) {
        e.target.value = 1;
      } else if (e.target.value > 6) {
        e.target.value = 6;
      }
    });