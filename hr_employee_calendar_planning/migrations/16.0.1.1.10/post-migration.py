from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    env["hr.employee"].cron_recompute_hours_per_day()
