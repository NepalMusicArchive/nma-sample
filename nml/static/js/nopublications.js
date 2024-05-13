
  $(document).ready(function() {
      $('#publicationTable').DataTable({
          "responsive": "true",
          "lengthChange": "false",
          "autowidth": "false",
          "serverSide": true,
          "ordering": false,
         
          "ajax": {
              "url": "/lib_publications/"+ qFromServer,
              "type": "GET",
              
          },
          "columns": [

              { "data": "title","orderable": true },           
              { "data": "author" },         
              { "data": "publisher" },
              { "data": "isbn" },
              { "data": "language" },
              { "data": "year" },
              { "data": "edition" },
              { "data": "category" },                
              {
                "data": null,
            "render": function (data, type, row) {
                
                // Other buttons
                var actionButtons = 

                '<img src="'+ row.lib_image_url +'" width="40em" class="rounded mx-auto d-block" data-bs-toggle="tooltip" data-bs-placement="left"'+
                ' title="'+data.library+'" alt="'+data.library+'"></img>' 
              
                return   actionButtons ;
            },
                
        },
             
              {
              "data": null,
          "render": function (data, type, row) {
              
              // Other buttons
              var actionButtons = 
              '<a href="' + row.detail_url + '"v>' +
                        '<button type="button" data-bs-toggle="tooltip" data-bs-placement="top" title="View Details" class="btn btn-outline-success btn-sm btn-sm">' +
                        '<i class="bi bi-card-heading"></i></button></a>' +
                        '<a href="' + row.edit_url + '"v>' +
                        '<button type="button" data-bs-toggle="tooltip" data-bs-placement="top" title="Edit Collection" class="btn btn-outline-primary btn-sm btn-sm">' +
                        '<i class="bi bi-pencil-square"></i></button></a>' +
                        '<a href="' + row.delete_url + '"v onclick="return confirm(\'Are you sure you want to delete this entry?\')">' +
                        '<button type="button" data-bs-toggle="tooltip" data-bs-placement="right" title="Delete Collection" class="btn btn-outline-danger btn-sm">' +
                        '<i class="bi bi-trash3-fill"></i></button></a>'+
                        '</form>';

            
              return   actionButtons ;
          },
              
      }
          
          ],
          dom: '<"top"fip>lrt<"bottom"p><"clear">',
  "pageLength": 20,
  "lengthMenu": [ 10, 20, 50, 75, 100 ],
  "pagingType": "simple_numbers", 
  "mark": true,
  "drawCallback": function(settings) {
              // Custom draw callback to update info in the table footer
              var api = this.api();
              var pageInfo = api.page.info();

              $('#start').html(pageInfo.start + 1);
              $('#end').html(pageInfo.end);
              $('#total').html(pageInfo.recordsDisplay);
              $('#totalRecords').html(pageInfo.recordsTotal);
              $('#recordsFiltered').html(pageInfo.recordsFiltered);
          }
      });
  });








  