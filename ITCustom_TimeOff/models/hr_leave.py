from odoo import fields, models, api

class CustomTimeOffReport(models.Model):
    _name = 'custom.timeoff.report'
    _description = 'Time Off Report with All Employees'
    _auto = False

    employee_id = fields.Many2one('hr.employee', string="Employee")
    employee_name = fields.Char(string="Employee Name")
    time_off_type = fields.Many2one('hr.leave.type', string="Time Off Type")
    total_days = fields.Float(string="Total Days")

    def init(self):
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW custom_timeoff_report AS (
                SELECT
                    e.id AS id,
                    e.id AS employee_id,
                    e.name AS employee_name,
                    lt.id AS time_off_type,
                    COALESCE(SUM(l.number_of_days), 0) AS total_days
                FROM
                    hr_employee e
                LEFT JOIN
                    hr_leave l ON l.employee_id = e.id AND l.state = 'validate'
                LEFT JOIN
                    hr_leave_type lt ON lt.id = l.holiday_status_id
                GROUP BY
                    e.id, e.name, lt.id
            )
        """)
