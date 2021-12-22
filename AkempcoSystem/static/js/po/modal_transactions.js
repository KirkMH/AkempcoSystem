    $('#item_add_form').submit(function(e) {
        e.preventDefault()
        let token = $("#item_add_form").find('input[name=csrfmiddlewaretoken]').val()
        
        // submit data using ajax
        let data = {
            'csrfmiddlewaretoken': token,
            'supplier_id': get_selected_id('id_supplier', false),
            'id_po_date': $('#id_po_date').val(),
            'id_promo_code': $('#id_promo_code').val(),
            'product_id': get_selected_id('product', true),
            'qty': $('#qty').val(),
            'supplier_price': $('#supplier_price').val()
        }
        $.ajax({
            url: '/po/ajax/save_item',
            type: 'POST',
            data: data,
            dataType: 'json',
            success: function(data) {
                location.href = data
            }
        })
    });
    
    
    function get_data() {
        let key = $('#search').val()
        // console.log("key="+key)
        $.ajax({
            url: '/po/ajax/load_data',
            type: 'GET',
            data: {
                'key': key,
                'supplier_id': get_selected_id('id_supplier', false)
            },
            dataType: 'json',
            success: function(data) {
                $('#product').empty()
                data.forEach(e => {
                    let id = e['id']
                    let name = e['full_description']
    
                    $('#product').append("<option value='" + id + "'>" + name + "</option")
                });
            }
        })
    }
    
    
    function update_po_item_data(id, value, field) {
        let token = $("#create_po").find('input[name=csrfmiddlewaretoken]').val()
        console.log(token)
        $.ajax({
            url: '/po/ajax/update_po_item_data',
            type: 'POST',
            data: {
                'csrfmiddlewaretoken': token,
                'id': id, 
                'value': value, 
                'field': field
            },
            dataType: 'json',
            success: function(data) {
                location.href = data
            }
        })
    }
    
    
    $('#search').keyup(function(e){
        if(e.keyCode == 13) {
            select_product()
        }
        else if (e.keyCode == 40) {
            $('#product').focus()
        }
        else
            get_data()
    });
    
    
    function get_selected_id(id, get_first_item = false) {
        let selected_value = $("#" + id).find(":selected").val();
        if (selected_value == undefined && get_first_item) {
            $("#product").prop("selectedIndex", 0);
            selected_value = $("#" + id).find(":selected").val();
        }
        return selected_value
    }
    function select_product() {
        let pk = get_selected_id('product', true)
        $.ajax({
            url: '/po/ajax/select_product',
            type: 'GET',
            data: {'pk': pk},
            dataType: 'json',
            success: function(data) {
                $('#supplier_price').val(data.supplier_price)
                $('#current_stocks').val(data.stocks)
                $('#order_uom').text(data.order_uom)
                $('#qty').focus()
            }
        })
    }
    $('#product').keyup(function(e) {
        if (e.keyCode == 13) {
            select_product()
        }
    });
    $('#product').click(function() {
        select_product()
    });
    
    $('#qty').keyup(function(e) {
        if (e.keyCode == 13)
            $('#item_add_form').trigger('submit')
    })
    $('#supplier_price').keyup(function(e) {
        if (e.keyCode == 13)
            $('#item_add_form').trigger('submit')
    })
    $('#add').click(function() {
        $('#item_add_form').trigger('submit')
    })
