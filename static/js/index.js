// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        edit_mode: false,
        add_mode: false,
        add_class_name: "",
        add_class_type: "",
        rows: [],
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => { e._idx = k++; });
        return a;
    };

    app.toggle_edit_mode = function() {
        app.vue.edit_mode = !app.vue.edit_mode;
    };

    app.save_table_changes = function() {
        entries = ['class_name', 'class_type', 'quarter_1', 'quarter_2', 'quarter_3', 'summer_1', 'summer_2', 'course_time_sections', 'actual_times'];
        // Update db
        for (let i = 0; i < app.vue.rows.length; ++i) {
            let row = app.vue.rows[i];
            for (const [key, value] of Object.entries(row)) {
                // console.log(key, value);
                if (entries.includes(key) && row._server_vals[key] !== value) {
                    // console.log(key);
                    axios.post(edit_class_url, {
                        id: row.id, field: key, value: value
                    }).then(function (result) {
                        // row._state[key] = "clean";
                        row._server_vals[key] = value;
                    });
                }
              }
        }
        // Exit Edit Mode
        app.toggle_edit_mode();
    };

    app.decorate = (a) => {
        a.map((e) => {
            e._state = { class_name: "clean", class_type: "clean", quarter_1: "clean", quarter_2: "clean", quarter_3: "clean", summer_1: "clean", summer_2: "clean" };
            e._server_vals = { class_name: e.class_name, class_type: e.class_type, quarter_1: e.quarter_1, quarter_2: e.quarter_2, quarter_3: e.quarter_3, summer_1: e.summer_1, summer_2: e.summer_2 };
        });
        return a;
    };

    app.add_class = function () {
        axios.post(add_class_url,
            {
                class_name: app.vue.add_class_name,
                class_type: app.vue.add_class_type,
                quarter_1: app.vue.add_quarter_1,
                quarter_2: app.vue.add_quarter_2,
                quarter_3: app.vue.add_quarter_3,
                summer_1: app.vue.add_summer_1,
                summer_2: app.vue.add_summer_2,
                _state: { class_name: "clean", class_type: "clean", quarter_1: "clean", quarter_2: "clean", quarter_3: "clean", summer_1: "clean", summer_2: "clean" },
            }).then(function (response) {
                app.vue.rows.push({
                    id: response.data.id,
                    class_name: app.vue.add_class_name,
                    class_type: app.vue.add_class_type,
                    quarter_1: app.vue.add_quarter_1,
                    quarter_2: app.vue.add_quarter_2,
                    quarter_3: app.vue.add_quarter_3,
                    summer_1: app.vue.add_summer_1,
                    summer_2: app.vue.add_summer_2,
                    _state: { class_name: "clean", class_type: "clean", quarter_1: "clean", quarter_2: "clean", quarter_3: "clean", summer_1: "clean", summer_2: "clean" },

                    _server_vals: {
                        class_name: app.vue.add_class_name,
                        class_type: app.vue.add_class_type,
                        quarter_1: app.vue.add_quarter_1,
                        quarter_2: app.vue.add_quarter_2,
                        quarter_3: app.vue.add_quarter_3,
                        summer_1: app.vue.add_summer_1,
                        summer_2: app.vue.add_summer_2,
                    }
                });
                app.enumerate(app.vue.rows);
                app.reset_form();
                app.set_add_status(false);
            });
    };

    app.reset_form = function () {
        class_name: app.vue.add_class_name="";
        class_type: app.vue.add_class_type="";
        quarter_1: app.vue.add_quarter_1="";
        quarter_2: app.vue.add_quarter_2="";
        quarter_3: app.vue.add_quarter_3="";
        summer_1: app.vue.add_summer_1="";
        summer_2: app.vue.add_summer_2="";
    };

    app.delete_class = function (row_idx) {
        let id = app.vue.rows[row_idx].id;
        axios.get(delete_class_url, { params: { id: id } }).then(function (response) {
            for (let i = 0; i < app.vue.rows.length; i++) {
                if (app.vue.rows[i].id === id) {
                    app.vue.rows.splice(i, 1);
                    app.enumerate(app.vue.rows);
                    break;
                }
            }
        });
    };

    app.set_add_status = function (new_status) {
        app.vue.add_mode = new_status;
    };

    app.start_edit = function (row_idx, fn) {
        if (app.vue.edit_mode) {
            app.vue.rows[row_idx]._state[fn] = "edit";
        }
    };

    app.stop_edit = function (row_idx, fn) {
        let row = app.vue.rows[row_idx];
        if (row._state[fn] === 'edit') {
            if (row._server_vals[fn] !== row[fn]) {
                // row._state[fn] = "pending";
                // axios.post(edit_class_url, {
                //     id: row.id, field: fn, value: row[fn]
                // }).then(function (result) {
                //     row._state[fn] = "clean";
                //     row._server_vals[fn] = row[fn];
                // })
                row._state[fn] = "clean";
            } else {
                row._state[fn] = "clean";
            }
        }
    };

    app.cancel_edit = function() {
        // Exit edit mode
        app.toggle_edit_mode();
        // TODO: reset table to previous values
    };

    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    app.methods = {
        toggle_edit_mode: app.toggle_edit_mode,
        save_table_changes: app.save_table_changes,
        add_class: app.add_class,
        set_add_status: app.set_add_status,
        delete_class: app.delete_class,
        start_edit: app.start_edit,
        stop_edit: app.stop_edit,
        cancel_edit: app.cancel_edit
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    // Generally, this will be a network call to the server to
    // load the data.
    // For the moment, we 'load' the data from a string.
    app.init = () => {
        axios.get(load_contacts_url).then(function (response) {
            app.vue.rows = app.decorate(app.enumerate(response.data.rows));
        });
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);