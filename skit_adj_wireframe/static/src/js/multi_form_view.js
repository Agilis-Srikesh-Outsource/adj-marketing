odoo.define('skit_adj_wireframe.multi_form_view', function (require) {
    "use strict";
    
    //var FormCommon = require('web.form_common');
    var core = require('web.core');
    var data = require('web.data');
    var _t = core._t;
    var view_dialogs = require('web.view_dialogs');
    var FormViewDialog = view_dialogs.FormViewDialog;
    
    view_dialogs.FormViewDialog.include({
    	init: function(parent, options) {
    		var self = this;

            this.res_id = options.res_id || null;
            this.on_saved = options.on_saved || (function () {});
            this.context = options.context;
            this.model = options.model;
            this.parentID = options.parentID;
            this.recordID = options.recordID;
            this.shouldSaveLocally = options.shouldSaveLocally;

            var multi_select = !_.isNumber(options.res_id) && !options.disable_multiple_selection;
            var readonly = _.isNumber(options.res_id) && options.readonly;

            if (!options || !options.buttons) {
                options = options || {};
                options.buttons = [{
                    text: (readonly ? _t("Close") : _t("Discard")),
                    classes: "btn-default o_form_button_cancel",
                    close: true,
                    click: function () {
                        if (!readonly) {
                            self.form_view.model.discardChanges(self.form_view.handle, {
                                rollback: self.shouldSaveLocally,
                            });
                        }
                    },
                }];

                if (!readonly) {
                    options.buttons.unshift({
                        text: _t("Save") + ((multi_select)? " " + _t(" & Close") : ""),
                        classes: "btn-primary",
                        click: function () {
                        	var record = self.form_view.model.get(self.form_view.handle);
                        	if (self.res_model == 'sale.order.line'){
                            	var data = record.data;
                                var product = data.product_id.data.id
                                var price_unit = data.price_unit
                                self._rpc({
                                    model: 'sale.order.line',
                                    method: 'change_unit_price',
                                    args: [0, price_unit, product],
                                }).then(function (result) {
                                	if(result == false){
                                		return self.do_action({
                                            type: 'ir.actions.act_window',
                                            res_model: 'skit.error',
                                            view_type: 'form',
                                            view_mode: 'form',
                                            views: [[false, 'form']],
                                            target: 'new'
                                        });
                                		//return self.do_warn(_t("Selling price should not be lesser than Gross Margin %."));
                                	}
                                	else{
                                		self._save().then(self.close.bind(self));
                                	}
                                },function(err,event){
                      	            event.preventDefault();
                      	            var err_msg = 'Please check the Internet Connection./n';
                      	            if(err.data.message)
                      	            	err_msg = err.data.message;
                      	        });
                            }
                        	else{
                        		this._save().then(self.close.bind(self));
                        	}
                        }
                    });

                    if (multi_select) {
                        options.buttons.splice(1, 0, {
                            text: _t("Save & New"),
                            classes: "btn-primary",
                            click: function () {
                                this._save().then(self.form_view.createRecord.bind(self.form_view, self.parentID));
                            },
                        });
                    }
                }
            }
            this._super(parent, options);
        },
        
        
    });
});
