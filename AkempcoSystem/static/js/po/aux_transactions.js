
    $('#add_item').click(function() {
        get_data()
        showModal()
    })

    function edit_item_qty(id, val) {
        console.log(id)
        bootbox.prompt({
            title: "Please enter the new quantity:",
            inputType: 'number',
            'value': val,
            callback: function (result) {
                response = update_po_item_data(id, result, 'quantity')
            }
        });
    }

    function edit_item_price(id, val) {
        console.log(id)
        bootbox.prompt({
            title: "Please enter the new unit price:",
            inputType: 'number',
            'value': val,
            'step': 0.01,
            callback: function (result) {
                if (result) {
                    response = update_po_item_data(id, result, 'unit_price')
                }
            }
        });
    }

    function showModal() {
        $('#modal').modal('show')
        $('#search').focus()
    }

    
    $('#save').click(function() {
        bootbox.confirm("Are you sure you want to save this purchase order?", function(result){ 
            if (result) {
                $("#clicked").val("save")
                $('#go').click()
            }
        });
    })

    $('#submit').click(function() {
        bootbox.confirm("Are you sure you want to submit this purchase order?", function(result){ 
            if (result) {
                $("#clicked").val("submit")
                $('#go').click()
            }
        });
    })

    $('#approve').click(function() {
        bootbox.confirm("Are you sure you want to approve this purchase order?", function(result){ 
            if (result) {
                $("#clicked").val("approve")
                $('#go').click()
            }
        });
    })