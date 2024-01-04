document.addEventListener('DOMContentLoaded', function () {
    var clickableCells = document.querySelectorAll('.clickable-cell');
    var editableCells = document.querySelectorAll('.editable-cell');

    clickableCells.forEach(function (cell) {
        cell.addEventListener('click', function () {
            var url = this.getAttribute('data-url');
            window.location.href = url;
        });
    });
  });