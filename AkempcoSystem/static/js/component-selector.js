$.ajax({
    url: "/ajax/component_permissions", 
    dataType: 'json',
    success: function(data){
        console.log(data)
        data.no_permissions.forEach(e => {
            let class_name = '.type' + e
            console.log(class_name)
            $(class_name).hide()
        });
    }
});