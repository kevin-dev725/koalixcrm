import datetime
import pytest
import pytz
from django.test import TestCase
from koalixcrm.crm.factories.factory_user import AdminUserFactory
from koalixcrm.crm.factories.factory_customer_billing_cycle import StandardCustomerBillingCycleFactory
from koalixcrm.crm.factories.factory_customer import StandardCustomerFactory
from koalixcrm.crm.factories.factory_customer_group import StandardCustomerGroupFactory
from koalixcrm.crm.factories.factory_currency import StandardCurrencyFactory
from koalixcrm.crm.factories.factory_reporting_period import StandardReportingPeriodFactory
from koalixcrm.djangoUserExtension.factories.factory_user_extension import StandardUserExtensionFactory
from koalixcrm.crm.factories.factory_work import StandardWorkFactory
from koalixcrm.crm.factories.factory_task import StandardTaskFactory
from koalixcrm.crm.factories.factory_employee_assignment_to_task import StandardEmployeeAssignmentToTaskFactory


class TaskPlannedEffort(TestCase):
    def setUp(self):
        datetime_now = datetime.datetime(2024, 1, 1, 0, 00)
        datetime_now = pytz.timezone("UTC").localize(datetime_now, is_dst=None)
        start_date = (datetime_now - datetime.timedelta(days=30)).date()
        end_date_first_task = (datetime_now + datetime.timedelta(days=30)).date()
        end_date_second_task = (datetime_now + datetime.timedelta(days=60)).date()

        self.test_billing_cycle = StandardCustomerBillingCycleFactory.create()
        self.test_user = AdminUserFactory.create()
        self.test_customer_group = StandardCustomerGroupFactory.create()
        self.test_customer = StandardCustomerFactory.create(is_member_of=(self.test_customer_group,))
        self.test_currency = StandardCurrencyFactory.create()
        self.test_user_extension = StandardUserExtensionFactory.create(user=self.test_user)
        self.test_reporting_period = StandardReportingPeriodFactory.create()
        self.test_1st_task = StandardTaskFactory.create(title="1st Test Task",
                                                        planned_start_date=start_date,
                                                        planned_end_date=end_date_first_task,
                                                        project=self.test_reporting_period.project)
        self.test_2nd_task = StandardTaskFactory.create(title="2nd Test Task",
                                                        planned_start_date=start_date,
                                                        planned_end_date=end_date_second_task,
                                                        project=self.test_reporting_period.project)

    @pytest.mark.back_end_tests
    def test_planned_effort(self):
        datetime_now = datetime.datetime(2024, 1, 1, 0, 00)
        datetime_now = pytz.timezone("UTC").localize(datetime_now, is_dst=None)
        datetime_later_1 = datetime.datetime(2024, 1, 1, 2, 00)
        datetime_later_1 = pytz.timezone("UTC").localize(datetime_later_1, is_dst=None)
        datetime_later_2 = datetime.datetime(2024, 1, 1, 3, 30)
        datetime_later_2 = pytz.timezone("UTC").localize(datetime_later_2, is_dst=None)
        datetime_later_3 = datetime.datetime(2024, 1, 1, 5, 45)
        datetime_later_3 = pytz.timezone("UTC").localize(datetime_later_3, is_dst=None)
        datetime_later_4 = datetime.datetime(2024, 1, 1, 6, 15)
        datetime_later_4 = pytz.timezone("UTC").localize(datetime_later_4, is_dst=None)
        date_now = datetime_now.date()
        self.assertEqual(
            (self.test_1st_task.planned_duration()).__str__(), "60")
        self.assertEqual(
            (self.test_1st_task.planned_effort()).__str__(), "0")
        self.assertEqual(
            (self.test_2nd_task.planned_duration()).__str__(), "90")
        self.assertEqual(
            (self.test_2nd_task.planned_effort()).__str__(), "0")
        StandardEmployeeAssignmentToTaskFactory.create(employee=self.test_user_extension,
                                                       planned_effort="2.00",
                                                       task=self.test_1st_task)
        StandardEmployeeAssignmentToTaskFactory.create(employee=self.test_user_extension,
                                                       planned_effort="1.50",
                                                       task=self.test_1st_task)
        StandardEmployeeAssignmentToTaskFactory.create(employee=self.test_user_extension,
                                                       planned_effort="4.75",
                                                       task=self.test_2nd_task)
        StandardEmployeeAssignmentToTaskFactory.create(employee=self.test_user_extension,
                                                       planned_effort="3.25",
                                                       task=self.test_2nd_task)
        self.assertEqual(
            (self.test_1st_task.planned_effort()).__str__(), "3.50")
        self.assertEqual(
            (self.test_1st_task.effective_effort(reporting_period=None)).__str__(), "0.0")
        self.assertEqual(
            (self.test_2nd_task.planned_effort()).__str__(), "8.00")
        self.assertEqual(
            (self.test_2nd_task.effective_effort(reporting_period=None)).__str__(), "0.0")
        StandardWorkFactory.create(
            employee=self.test_user_extension,
            date=date_now,
            start_time=datetime_now,
            stop_time=datetime_later_1,
            task=self.test_1st_task,
            reporting_period=self.test_reporting_period)
        StandardWorkFactory.create(
            employee=self.test_user_extension,
            date=date_now,
            start_time=datetime_later_1,
            stop_time=datetime_later_2,
            task=self.test_1st_task,
            reporting_period=self.test_reporting_period)
        StandardWorkFactory.create(
            employee=self.test_user_extension,
            date=date_now,
            start_time=datetime_now,
            stop_time=datetime_later_3,
            task=self.test_2nd_task,
            reporting_period=self.test_reporting_period
        )
        StandardWorkFactory.create(
            employee=self.test_user_extension,
            date=date_now,
            start_time=datetime_now,
            stop_time=datetime_later_4,
            task=self.test_2nd_task,
            reporting_period=self.test_reporting_period
        )
        self.assertEqual(
            (self.test_1st_task.effective_effort(reporting_period=None)).__str__(), "3.5")
        self.assertEqual(
            (self.test_2nd_task.effective_effort(reporting_period=None)).__str__(), "12.0")
        self.assertEqual(
            (self.test_reporting_period.project.effective_effort(reporting_period=None)).__str__(), "15.5")
        self.assertEqual(
            (self.test_reporting_period.project.planned_effort()).__str__(), "11.50")
