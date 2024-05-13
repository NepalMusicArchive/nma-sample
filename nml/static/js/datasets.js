  $(document).ready(function() {
      $('#TimelineTable').DataTable({
          "responsive": "true",
          "lengthChange": "false",
          "ordering": false,
          "autowidth": "false",
          "serverSide": true,
          processing: true,
          "ajax": {
              "url": "/get_timeline",
              "type": "GET",
              
          },
          "columns": [
              // Define your columns as needed

              { "data": "title","orderable": true ,
                    "render": function (data, type, row) {
                        if (type === 'display' && data) {
                        var maxLength = 20; // Change this to your desired maximum number of characters

                        // Truncate if more than maxLength characters
                        var truncatedText = data.length > maxLength ? data.slice(0, maxLength) + '...' : data;

                        return truncatedText;
                    }

                    return data;
                },
            },           
              { "data": "releasedate" },         
              { "data": "description" 
            },
              { "data": "group" },
             
              {
              "data": null,
          "render": function (data, type, row) {
              
              // Other buttons
              var actionButtons = 
                  '<a href="' + row.edit_url + '">' +
                  '<button type="button" data-bs-toggle="tooltip" data-bs-placement="top" title="Edit Collection" class="btn btn-outline-primary btn-sm btn-sm">' +
                  '<i class="bi bi-pencil-square"></i></button></a>' +
                  '<a href="' + row.delete_url + '" onclick="return confirm(\'Are you sure you want to delete this entry?\')">' +
                  '<button type="button" data-bs-toggle="tooltip" data-bs-placement="right" title="Delete Collection" class="btn btn-outline-danger btn-sm">' +
                  '<i class="bi bi-trash3-fill"></i></button></a>';

            
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



  