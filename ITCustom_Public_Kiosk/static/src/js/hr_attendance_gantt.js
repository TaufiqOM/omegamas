import { GanttRenderer } from "@web_gantt/views/gantt_renderer";



GanttRenderer.include({
    _renderBar: function (task) {
        var $bar = this._super.apply(this, arguments);
        if (task.record.terlambat === 1) {
            $bar.css('background-color', 'blue');
        }
        return $bar;
    },
});
