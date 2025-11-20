var updateBtns = document.getElementsByClassName('producto-renta')

for (i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', function() {
        var productId = this.dataset.product
        var action = this.dataset.action
        console.log('productId:', productId, 'action:', action)

        updateUserOrder(productId, action, true)
    })
}

var startBtn = document.getElementsByClassName('producto-inicio')

for (i = 0; i < startBtn.length; i++) {
    startBtn[i].addEventListener('click', function() {
        var productId = this.dataset.product
        var action = this.dataset.action
        console.log('productId:', productId, 'action:', action)

        updateUserOrder(productId, action, false)
    })
}

function updateUserOrder(productId, action, reload) {
    var url = '/actualizarrenta/'

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({'productId': productId, 'action': action})
    })
    .then((response) => {
        return response.json();
    })
    .then((data) => {
        if (reload) {
            location.reload();
        }
    })
}
