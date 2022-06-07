// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        // Complete as you see fit.
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
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
    
    app.toggle_edit_mode = function() {
        app.vue.edit_mode = !app.vue.edit_mode;
    };

    app.start_edit = function (table, row_idx, fn) {
        if (app.vue.edit_mode) {
            table = table == app.data.rows ? app.vue.rows : app.vue.rows_i;
            table[row_idx]._state[fn] = "edit";
        }
    };

    app.stop_edit = function (table, row_idx, fn) {
        table = table == app.data.rows ? app.vue.rows : app.vue.rows_i;
        let row = table[row_idx];
        if (row._state[fn] === 'edit') {
            console.log(row._server_vals[fn]);
            if (row._server_vals[fn] !== row[fn]) {
                // TODO: change to some other visual indicator
                row._state[fn] = "edit";
            } else {
                row._state[fn] = "clean";
            }
        }
        // added a warning feature verification in the stop edit function
        //so after the edit is done, items will be highlighted
    
        // a dummy case to show that it works
        if (row[fn] === "test"){
            row.is_error = true
    
        };
    };
    // boiler plate for setting an error function outside of scope
    // app.set_error =  function (row_idx, fn) {
    //     let row = app.vue.rows[row_idx];
    //     if(row[fn] === undefined) {
    //         alert("myProperty value is the special value `undefined`");
    //       }
    //     if (row[fn] === "test"){
    //         row.is_error = true
    
    //     };
    //     console.log(row.last_name)
    //     console.log(row.is_error)
    // };

    app.cancel_edits = function() {
        app.cancel_edit(app.data.rows);
        app.cancel_edit(app.data.rows_i);

        // Exit edit mode
        app.toggle_edit_mode();
    }

    app.cancel_edit = function(table) {
        entries = ['class_name', 'class_type', 'quarter_1', 'quarter_2', 'quarter_3', 'summer_1', 'summer_2', 'course_time_sections', 'actual_times'];
        // Reset table to current server values
        table == app.data.rows ? app.vue.rows : app.vue.rows_i; 
        for (let i = 0; i < table.length; ++i) {
            let row = table[i];
            for (const [key, value] of Object.entries(row)) {
                if (entries.includes(key) && row._server_vals[key] !== value) {
                    row[key] = row._server_vals[key];
                    row._state[key] = "clean";
                }
              }
        }
    };

    app.save_table_changes = function() {
        entries = ['class_name', 'class_type', 'quarter_1', 'quarter_2', 'quarter_3', 'summer_1', 'summer_2', 'course_time_sections', 'actual_times'];
        // Update db
        for (let i = 0; i < app.vue.rows.length; ++i) {
            let row = app.vue.rows[i];
            for (const [key, value] of Object.entries(row)) {
                if (entries.includes(key) && row._server_vals[key] !== value) {
                    row._state[key] = "pending";
                    axios.post(edit_class_url, {
                        id: row.id, field: key, value: value
                    }).then(function (result) {
                        row._state[key] = "clean";
                        row._server_vals[key] = value;
                    });
                }
              }
        }
        // Exit Edit Mode
        app.toggle_edit_mode();
    };

    app.set_error =  function (row_idx) {
        let row = app.vue.rows[row_idx];
        if (row.last_name === "test"){
            row.is_error = "true"
    
        };
        console.log(row.is_error)
    };


    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    app.methods = {
        toggle_edit_mode: app.toggle_edit_mode,
        save_table_changes: app.save_table_changes,
        add_class: app.add_class,
        add_instructor: app.add_instructor,
        set_add_status: app.set_add_status,
        delete_class: app.delete_class,
        start_edit: app.start_edit,
        stop_edit: app.stop_edit,
        cancel_edit: app.cancel_edit,
        cancel_edits: app.cancel_edits
        //set_error: app.set_error,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        // Put here any initialization code.
        // Typically this is a server GET call to load the data.
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
