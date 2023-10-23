from datetime import datetime

from odoo.addons.hr_contract.tests.common import TestContractCommon

from ..hooks import post_init_hook


class TestHrContractEmployeeCalendarPlanning(TestContractCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                mail_create_nolog=True,
                mail_create_nosubscribe=True,
                mail_notrack=True,
                no_reset_password=True,
                tracking_disable=True,
            )
        )
        calendar_ids = [
            (
                0,
                0,
                {
                    "date_start": False,
                    "date_end": datetime.strptime("2020-11-30", "%Y-%m-%d").date(),
                    "calendar_id": cls.env["resource.calendar"].browse([2]).id,
                },
            ),
            (
                0,
                0,
                {
                    "date_start": datetime.strptime("2020-12-01", "%Y-%m-%d").date(),
                    "date_end": False,
                    "calendar_id": cls.env["resource.calendar"].browse([1]).id,
                },
            ),
        ]
        cls.employee.calendar_ids = calendar_ids

    def test_calendar_migration_from_contracts(self):
        # newly created contracts get the same calendar as the employee
        self.employee.resource_calendar_id = self.env["resource.calendar"].browse([1])
        self.env["hr.contract"].create(
            {
                "name": "contract1",
                "wage": 1,
                "state": "close",
                "employee_id": self.employee.id,
                "date_start": datetime.strptime("2018-11-30", "%Y-%m-%d").date(),
                "date_end": datetime.strptime("2019-11-30", "%Y-%m-%d").date(),
            }
        )
        self.employee.resource_calendar_id = self.env["resource.calendar"].browse([2])
        self.env["hr.contract"].create(
            {
                "name": "contract2",
                "wage": 1,
                "state": "open",
                "employee_id": self.employee.id,
                "date_start": datetime.strptime("2019-12-01", "%Y-%m-%d").date(),
                "date_end": datetime.strptime("2020-11-30", "%Y-%m-%d").date(),
            }
        )
        calendar_ids = self.env["hr.employee.calendar"].create(
            [
                {
                    "date_start": False,
                    "date_end": datetime.strptime("2020-11-30", "%Y-%m-%d").date(),
                    "calendar_id": 2,
                    "employee_id": self.employee.id,
                },
                {
                    "date_start": datetime.strptime("2020-12-01", "%Y-%m-%d").date(),
                    "date_end": False,
                    "calendar_id": 1,
                    "employee_id": self.employee.id,
                },
            ]
        )
        self.employee.calendar_ids = [(6, 0, calendar_ids.ids)]
        start_dt = datetime(2019, 1, 1, 0, 0, 0)
        end_dt = datetime(2019, 1, 2, 0, 0, 0)
        self.assertEqual(
            7.0,
            self.employee.resource_calendar_id.get_work_hours_count(
                start_dt=start_dt,
                end_dt=end_dt,
            ),
        )
        # calendar migration from contracts
        post_init_hook(self.env.cr, self.env.registry, self.employee)
        self.assertEqual(
            8.0,
            self.employee.resource_calendar_id.get_work_hours_count(
                start_dt=start_dt,
                end_dt=end_dt,
            ),
        )
        self.assertTrue(calendar_ids.ids < self.employee.calendar_ids.ids)
