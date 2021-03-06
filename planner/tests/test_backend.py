import datetime
import json

from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse

from planner.tests import test_index
from ..models import Plan, Place, MAX_DAYS_PER_PLAN, MAX_PLACES_PER_DAY
from ..views import MAX_PLACE_PER_REQUEST


class BackendPostMethodTest(test_index.ViewTest):
    """Tests for ajax calling POST method to server."""

    def setUp(self):
        """Initialize planner, user and places in a plan."""
        super().setUp()
        self.place_details1 = {
            'day': 1,
            'sequence': 1,
            'place_id': "5678",
            'place_name': "Kasetsart",
            'place_vicinity': "Bangkok"
        }
        self.place1 = Place.objects.create(day=self.place_details1['day'],
                                           sequence=self.place_details1['sequence'],
                                           place_id=self.place_details1['place_id'],
                                           place_name=self.place_details1['place_name'],
                                           place_vicinity=self.place_details1['place_vicinity'],
                                           departure_time=datetime.time(0, 0),
                                           plan=self.plan)
        self.place_details2 = {
            'day': 1,
            'sequence': 2,
            'place_id': "9012",
            'place_name': "Central Ladprao",
            'place_vicinity': "Bangkok"
        }
        self.place2 = Place.objects.create(day=self.place_details2['day'],
                                           sequence=self.place_details2['sequence'],
                                           place_id=self.place_details2['place_id'],
                                           place_name=self.place_details2['place_name'],
                                           place_vicinity=self.place_details2['place_vicinity'],
                                           departure_time=datetime.time(0, 0),
                                           plan=self.plan)
        self.place1.save()
        self.place2.save()

    def test_change_name(self):
        """Test changing planner name."""
        new_name = "NewPlan"
        response = self.client.post(reverse("planner:post_edit"),
                                    {'planner_id': self.plan.id, 'name': new_name})
        self.assertEqual(json.loads(response.content)['status'], "OK")
        new_plan_status = Plan.objects.get(pk=self.plan.id)  # get current plan with new information
        self.assertEqual(new_plan_status.name, new_name)

    def test_change_days(self):
        """Test changing planner days."""
        new_days = MAX_DAYS_PER_PLAN
        response = self.client.post(reverse("planner:post_edit"),
                                    {'planner_id': self.plan.id, 'days': new_days})
        self.assertEqual(json.loads(response.content)['status'], "OK")
        new_plan_status = Plan.objects.get(pk=self.plan.id)  # get current plan with new information
        self.assertEqual(new_plan_status.days, new_days)

    def test_change_invalid_days(self):
        """Test changing planner days to invalid amount
        that can be in situation that over the limit od days or be negative."""
        # Test changing over limit.
        new_days = MAX_DAYS_PER_PLAN + 10
        response = self.client.post(reverse("planner:post_edit"),
                                    {'planner_id': self.plan.id, 'days': new_days})
        self.assertEqual(json.loads(response.content)['status'], "OK")
        new_plan_status = Plan.objects.get(pk=self.plan.id)  # get current plan with new information
        self.assertEqual(new_plan_status.days, MAX_DAYS_PER_PLAN)  # should be changed to MAX_DAYS_PER_PLAN

        # Test changing to negative value.
        new_days = -4
        response = self.client.post(reverse("planner:post_edit"),
                                    {'planner_id': self.plan.id, 'days': new_days})
        self.assertEqual(json.loads(response.content)['status'], "OK")
        new_plan_status = Plan.objects.get(pk=self.plan.id)  # get current plan with new information
        self.assertEqual(new_plan_status.days, 1)  # should be changed to 1

    def test_change_publish(self):
        """Test changing publish status."""
        if self.plan.status == 0:
            new_status = 1
        else:
            new_status = 0
        response = self.client.post(reverse("planner:post_edit"),
                                    {'planner_id': self.plan.id, 'publish': new_status})
        self.assertEqual(json.loads(response.content)['status'], "OK")
        new_plan_status = Plan.objects.get(pk=self.plan.id)  # get current plan with new information
        self.assertEqual(new_plan_status.status, new_status)

    def test_add_place_to_the_plan(self):
        """Test adding a place to the current plan."""
        new_place_day = 1
        new_place_sequence = self.plan.place_set.all().count() + 1
        new_place = {"day": new_place_day,
                     "sequence": new_place_sequence,
                     "place_id": "5678",
                     "place_name": "Central Ladprao",
                     "place_vicinity": "Bangkok",
                     "arrival_time": "",
                     "departure_time": "00:00"}
        response = self.client.post(reverse("planner:post_edit"),
                                    {'planner_id': self.plan.id, 'addPlace': json.dumps(new_place)})
        self.assertEqual(json.loads(response.content)['status'], "OK")
        # get new place with new information
        new_place_status = Place.objects.get(plan=self.plan.id, day=new_place_day, sequence=new_place_sequence)
        self.assertEqual(new_place_status.place_id, new_place['place_id'])
        self.assertEqual(new_place_status.place_name, new_place['place_name'])

    def test_add_invalid_place_argument(self):
        """Test add place to the database without specify day."""
        new_place_sequence = 10
        new_place = {"sequence": new_place_sequence,
                     "place_id": "5678",
                     "place_name": "Central Ladprao",
                     "place_vicinity": "Bangkok",
                     "arrival_time": "",
                     "departure_time": "00:00"}
        response = self.client.post(reverse("planner:post_edit"),
                                    {'planner_id': self.plan.id, 'addPlace': json.dumps(new_place)})
        self.assertEqual(json.loads(response.content)['status'], "Day not provided.")

    def test_add_place_with_missing_info(self):
        """Test adding place into a plan with missing some not important data."""
        new_place_day = 1
        new_place_sequence = self.plan.place_set.all().count() + 1
        new_place = {"day": new_place_day,
                     "sequence": new_place_sequence,
                     "place_id": "5678"}
        response = self.client.post(reverse("planner:post_edit"),
                                    {'planner_id': self.plan.id, 'addPlace': json.dumps(new_place)})
        self.assertEqual(json.loads(response.content)['status'], "OK")

    def test_add_place_with_arrival(self):
        """Test adding a place to the plan with specified arrival time."""
        new_place_day = 1
        new_place_sequence = self.plan.place_set.all().count() + 1
        new_place_hour = 9
        new_place_minute = 11
        new_place = {"day": new_place_day,
                     "sequence": new_place_sequence,
                     "place_id": "5678",
                     "place_name": "Central Ladprao",
                     "place_vicinity": "Bangkok",
                     "arrival_time": f"{str(new_place_hour).zfill(2)}:{str(new_place_minute).zfill(2)}",
                     "departure_time": "10:12"}
        response = self.client.post(reverse("planner:post_edit"),
                                    {'planner_id': self.plan.id, 'addPlace': json.dumps(new_place)})
        self.assertEqual(json.loads(response.content)['status'], "OK")
        # get new place with new information
        new_place_status = Place.objects.get(plan=self.plan.id, day=new_place_day, sequence=new_place_sequence)
        self.assertEqual(new_place_status.arrival_time, datetime.time(new_place_hour, new_place_minute))
        self.assertEqual(new_place_status.place_id, new_place['place_id'])
        self.assertEqual(new_place_status.place_name, new_place['place_name'])

    def test_delete_place_from_plan(self):
        """Test deleting a place from the plan."""
        response = self.client.post(reverse("planner:post_edit"),
                                    {'planner_id': self.plan.id, 'delPlace': json.dumps(self.place_details1)})
        self.assertEqual(json.loads(response.content)['status'], "OK")
        # get new status of planner, shouldn't be any place in the plan.
        new_plan_status = Plan.objects.get(pk=self.plan.id)
        with self.assertRaises(ObjectDoesNotExist):
            new_plan_status.place_set.get(pk=self.place1.id)

    def test_delete_place_not_exist_from_plan(self):
        """Test deleting a place from the plan which place order is incorrect."""
        self.place_details1['sequence'] = 2
        response = self.client.post(reverse("planner:post_edit"),
                                    {'planner_id': self.plan.id, 'delPlace': json.dumps(self.place_details1)})
        self.assertEqual(json.loads(response.content)['status'], "Place not found.")

    def test_move_place_up(self):
        """Test moving place up to previous sequence."""
        self.place_details2['day_moved'] = False
        response = self.client.post(reverse("planner:post_edit"),
                                    {'planner_id': self.plan.id, 'moveUp': json.dumps(self.place_details2)})
        self.assertEqual(json.loads(response.content)['status'], "OK")
        # get new status of planner, only sequence should change.
        new_plan_status = Plan.objects.get(pk=self.plan.id)
        new_plan_status.place_set.get(place_name=self.place_details2['place_name'],
                                      day=self.place_details2['day'],
                                      sequence=self.place_details2['sequence'] - 1)

    def test_move_place_down(self):
        """Test moving place down to next sequence."""
        self.place_details1['day_moved'] = False
        response = self.client.post(reverse("planner:post_edit"),
                                    {'planner_id': self.plan.id, 'moveDown': json.dumps(self.place_details1)})
        self.assertEqual(json.loads(response.content)['status'], "OK")
        # get new status of planner, only sequence should change.
        new_plan_status = Plan.objects.get(pk=self.plan.id)
        new_plan_status.place_set.get(place_name=self.place_details1['place_name'],
                                      day=self.place_details1['day'],
                                      sequence=self.place_details1['sequence'] + 1)

    def test_move_place_up_and_change_day(self):
        """Test moving place up to previous day."""
        new_place_details = {
            'day': 2,
            'sequence': 1,
            'place_id': "9012",
            'place_name': "Central World",
            'place_vicinity': "Bangkok",
            'day_moved': True,
            'day_destination': 1
        }
        new_place = Place.objects.create(day=new_place_details['day'],
                                         sequence=new_place_details['sequence'],
                                         place_id=new_place_details['place_id'],
                                         place_name=new_place_details['place_name'],
                                         place_vicinity=new_place_details['place_vicinity'],
                                         departure_time=datetime.time(0, 0),
                                         plan=self.plan)
        new_place.save()
        response = self.client.post(reverse("planner:post_edit"),
                                    {'planner_id': self.plan.id, 'moveUp': json.dumps(new_place_details)})
        self.assertEqual(json.loads(response.content)['status'], "OK")
        # get new status of planner, sequence and day should change.
        new_plan_status = Plan.objects.get(pk=self.plan.id)
        new_plan_status.place_set.get(place_name=new_place_details['place_name'],
                                      day=new_place_details['day_destination'])

    def test_move_place_down_to_next_day(self):
        """Test moving place down to next day."""
        self.place_details2['day_destination'] = 2
        self.place_details2['day_moved'] = True
        response = self.client.post(reverse("planner:post_edit"),
                                    {'planner_id': self.plan.id, 'moveDown': json.dumps(self.place_details2)})
        self.assertEqual(json.loads(response.content)['status'], "OK")
        # get new status of planner, sequence and day should change.
        new_plan_status = Plan.objects.get(pk=self.plan.id)
        new_plan_status.place_set.get(place_name=self.place_details2['place_name'],
                                      day=self.place_details2['day_destination'])

    def test_invalid_place_move_up(self):
        """Test move up invalid place. Should do nothing and return Place not found."""
        self.place_details2['day_moved'] = False
        self.place_details2['sequence'] = 3
        response = self.client.post(reverse("planner:post_edit"),
                                    {'planner_id': self.plan.id, 'moveUp': json.dumps(self.place_details2)})
        self.assertEqual(json.loads(response.content)['status'], "Place not found.")

    def test_invalid_place_move_down(self):
        """Test move down invalid place. Should do nothing and return Place not found."""
        self.place_details2['day_moved'] = False
        self.place_details2['sequence'] = 3
        response = self.client.post(reverse("planner:post_edit"),
                                    {'planner_id': self.plan.id, 'moveDown': json.dumps(self.place_details2)})
        self.assertEqual(json.loads(response.content)['status'], "Place not found.")

    def test_change_time(self):
        """Test changing arrival and departure time for each place."""
        self.place_details1['arrival'] = "10:00"
        self.place_details1['departure'] = "10:30"
        self.place_details2['arrival'] = "11:00"
        self.place_details2['departure'] = "11:30"
        response = self.client.post(reverse("planner:post_edit"),
                                    {'planner_id': self.plan.id,
                                     'changeTime': json.dumps([self.place_details1, self.place_details2])})
        self.assertEqual(json.loads(response.content)['status'], "OK")
        # get new status of planner, only time should change.
        new_plan_status = Plan.objects.get(pk=self.plan.id)
        new_place_details1 = new_plan_status.place_set.get(place_name=self.place_details1['place_name'],
                                                           day=self.place_details1['day'],
                                                           sequence=self.place_details1['sequence'])
        new_place_details2 = new_plan_status.place_set.get(place_name=self.place_details2['place_name'],
                                                           day=self.place_details2['day'],
                                                           sequence=self.place_details2['sequence'])
        self.assertEqual(new_place_details1.arrival_time, datetime.time(10, 0))
        self.assertEqual(new_place_details1.departure_time, datetime.time(10, 30))
        self.assertEqual(new_place_details2.arrival_time, datetime.time(11, 0))
        self.assertEqual(new_place_details2.departure_time, datetime.time(11, 30))

    def test_change_time_without_detail(self):
        """Test changing arrival and departure time for each place without specify arrival time."""
        self.place_details1['arrival'] = ""
        self.place_details1['departure'] = "10:30"
        self.place_details2['arrival'] = ""
        self.place_details2['departure'] = "11:30"
        response = self.client.post(reverse("planner:post_edit"),
                                    {'planner_id': self.plan.id,
                                     'changeTime': json.dumps([self.place_details1, self.place_details2])})
        self.assertEqual(json.loads(response.content)['status'], "OK")
        # get new status of planner, only time should change.
        new_plan_status = Plan.objects.get(pk=self.plan.id)
        new_place_details1 = new_plan_status.place_set.get(place_name=self.place_details1['place_name'],
                                                           day=self.place_details1['day'],
                                                           sequence=self.place_details1['sequence'])
        new_place_details2 = new_plan_status.place_set.get(place_name=self.place_details2['place_name'],
                                                           day=self.place_details2['day'],
                                                           sequence=self.place_details2['sequence'])
        self.assertEqual(new_place_details1.arrival_time, None)
        self.assertEqual(new_place_details1.departure_time, datetime.time(10, 30))
        self.assertEqual(new_place_details2.arrival_time, None)
        self.assertEqual(new_place_details2.departure_time, datetime.time(11, 30))

    def test_change_time_contains_invalid_place(self):
        """Test change time with incorrect position in database."""
        place_details1_backup = self.place_details1.copy()
        self.place_details1['arrival'] = "10:00"
        self.place_details1['day'] = 3
        self.place_details1['departure'] = "10:30"
        self.place_details2['arrival'] = "10:45"
        self.place_details2['departure'] = "11:30"
        response = self.client.post(reverse("planner:post_edit"),
                                    {'planner_id': self.plan.id,
                                     'changeTime': json.dumps([self.place_details1, self.place_details2])})
        self.assertEqual(json.loads(response.content)['status'], "OK")
        # get new status of planner, only second place should change.
        self.place_details1 = place_details1_backup.copy()
        new_plan_status = Plan.objects.get(pk=self.plan.id)
        new_place_details1 = new_plan_status.place_set.get(place_name=self.place_details1['place_name'],
                                                           day=self.place_details1['day'],
                                                           sequence=self.place_details1['sequence'])
        new_place_details2 = new_plan_status.place_set.get(place_name=self.place_details2['place_name'],
                                                           day=self.place_details2['day'],
                                                           sequence=self.place_details2['sequence'])
        # arrival and departure shouldn't change for first place.
        self.assertEqual(new_place_details1.arrival_time, None)
        self.assertEqual(new_place_details1.departure_time, datetime.time(0, 0))
        self.assertEqual(new_place_details2.arrival_time, datetime.time(10, 45))
        self.assertEqual(new_place_details2.departure_time, datetime.time(11, 30))

    def test_invalid_get_travel_time(self):
        """Test invalid context calling function get_travel_time()"""
        # testing context contains places more than MAX_PLACE_PER_REQUEST
        context = [{"place_id": "HelloWorld"} for _ in range(MAX_PLACE_PER_REQUEST + 5)]
        response = self.client.post(reverse("planner:get_travel_time"),
                                    {'places': json.dumps(context)})
        self.assertEqual(json.loads(response.content)['status'], "TOO MANY PLACES")

        # testing context contains only 1 place so it cannot get direction.
        context = [{"place_id": "HelloWorld"}]
        response = self.client.post(reverse("planner:get_travel_time"),
                                    {'places': json.dumps(context)})
        self.assertEqual(json.loads(response.content)['status'], "NOT ENOUGH PLACE")
