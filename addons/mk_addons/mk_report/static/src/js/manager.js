odoo.define('report_manager.manager', function(require) {
"use strict";

var core = require('web.core');
var session = require('web.session');
var FormController = require('web.FormController');
var FormView = require('web.FormView');
var Sidebar = require('web.Sidebar');

var _t = core._t;
var _lt = core._lt;
var QWeb = core.qweb;

FormView.include({
    /**
     * @override
     */
    init: function (viewInfo) {
        this._super.apply(this, arguments);
        this.controllerParams.viewID = viewInfo.view_id;
    },
});

FormController.include({
    init: function (parent, model, renderer, params) {
        this._super.apply(this, arguments);
        this.viewID = params.viewID;
        this.toolbarActions = params.toolbarActions || {};
    },
    _onReportManager: function(event) {
        var record = this.model.get(this.handle, {raw: true})
        return this.do_action({
            res_model: 'ir.actions.report',
            name: _t('Report'),
            domain: [['model', '=', this.modelName]],
            views: [[false, 'list'], [false, 'form']],
            type: 'ir.actions.act_window',
            view_type: 'list',
            view_mode: 'list',
            target: 'current',
            context: {
                'active_id': record.res_id,
                'active_model': record.model,
            }
        });
    },
    renderSidebar: function ($node) {
        this._super($node);
        if (this.sidebar && this.hasSidebar) {
            this.sidebar._addItems('other', [{
                callback: this._onReportManager.bind(this),
                label: _t('Report Manager'),
            }]);
            this.sidebar._redraw();
        }
    },
});

});
