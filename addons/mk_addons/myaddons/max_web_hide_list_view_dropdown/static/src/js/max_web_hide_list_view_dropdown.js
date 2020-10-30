odoo.define('max_web_hide_list_view_dropdown.max_web_hide_list_view_dropdown', function (require) {
'use strict';
    var session = require('web.session');
    var ListView = require('web.ListView');

     ListView.include({
        render_sidebar: function() {
            var self = this;
            this._super.apply(this, arguments);
            if (session.uid != 1)
                if (self.sidebar)
                    self.sidebar.hideExport();
        },
    });
});
