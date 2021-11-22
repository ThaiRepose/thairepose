/**
 * Check that if there's a place that arrival time is in the next day.
 */
function checkOverDate() {
  let lastDay = 1;
  let thisDay = 0;
  $.each($('[id^="table-day-"]'), function(key, table) {
    const places = $(table).find('[name^="arrival"]');
    let overDate = false;
    let firstPlace = true;
    let lastTime = null;
    thisDay++;
    $.each(places, function(index, date) {
      if (firstPlace) {
        const newTime = createTime($(date)[0].innerText);
        $(date)[0].setAttribute('value', newTime);
        firstPlace = false;
      }
      const arrivalDate = new Date($(date)[0].getAttribute('value'));
      // Adding notice blink.
      if (overDate) {
        // if last place is arrived in next day.
        date.closest('tr').classList.add('bg-red-400', 'blink-bg');
      } else if ($(date)[0].innerText === '') {
        // if there's no arrival time.
        date.closest('tr').classList.remove('bg-red-400', 'blink-bg');
        overDate = false;
      } else if (arrivalDate.getDate() > 1) {
        // if arrival time is in next day.
        date.closest('tr').classList.add('bg-red-400', 'blink-bg');
        overDate = true;
      } else if (arrivalDate < lastTime && lastDay === thisDay) {
        // if arrival time is less than the last.
        date.closest('tr').classList.add('bg-red-400', 'blink-bg');
        overDate = true;
      } else {
        date.closest('tr').classList.remove('bg-red-400', 'blink-bg');
        overDate = false;
      }
      lastTime = arrivalDate;
    });
    lastDay = thisDay;
  });
}

/**
 * Create Time object from a string. e.g. `13:00`.
 * @param {string} timeStr - time in format of 24-hours separate with `:`.
 * @return {Date} - datetime object from time.
 */
function createTime(timeStr) {
  // create a time with all the same date.
  const time = new Date('1970-01-01T' + timeStr + ':00Z');
  // set to current timezone.
  time.setTime(time.getTime() + time.getTimezoneOffset() * 60 * 1000);
  return time;
}

/**
 * Get time in string format. e.g. `15:00`.
 * @param {Date} timeObj - datetime object to get time.
 * @return {string} - time only in string of datetime.
 */
function getTimeFormat(timeObj) {
  return timeObj.toTimeString().replace(/.*(\d{2}:\d{2}):\d{2}.*/, '$1');
}