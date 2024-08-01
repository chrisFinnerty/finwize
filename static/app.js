document.addEventListener('DOMContentLoaded', function() {
    var transactionModal = document.getElementById('transactionModal');
    transactionModal.addEventListener('show.bs.modal', function (event) {
        var button = event.relatedTarget;
        var categoryId = button.getAttribute('data-category-id');
        var subcategoryId = button.getAttribute('data-subcategory-id');

        var categoryInput = document.getElementById('categoryInput');
        var subcategoryInput = document.getElementById('subcategoryInput');

        // Set selected options
        for (var i = 0; i < categoryInput.options.length; i++) {
            if (categoryInput.options[i].value === categoryId) {
                categoryInput.options[i].selected = true;
                break;
            }
        }

        for (var i = 0; i < subcategoryInput.options.length; i++) {
            if (subcategoryInput.options[i].value === subcategoryId) {
                subcategoryInput.options[i].selected = true;
                break;
            }
        }
    });
});