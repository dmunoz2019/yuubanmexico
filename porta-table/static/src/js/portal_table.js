/* @odoo-module */
odoo.define('portal.portal', function (require) {
    'use strict';
    
    var publicWidget = require('web.public.widget');
    const Dialog = require('web.Dialog');
    const {_t, qweb} = require('web.core');
    const session = require('web.session');

    publicWidget.registry.portalTable = publicWidget.Widget.extend({
        selector: '.portal_table',
        start: function () {
            console.log('portal_table');
        }
    });

});
