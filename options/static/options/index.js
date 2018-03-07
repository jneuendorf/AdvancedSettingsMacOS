import commandConfig from './commands.js'


$('.commands').css({
    minHeight: `${$("aside").height()}px`,
    maxHeight: `${window.innerHeight - 2*48}px`,
})

$('.store-password').click(event => {
    const password = prompt('Tell me your password!')
    if (password != null) {
        fetch('store_password/', {
            headers: {
                'Content-Type': 'text/plain; charset=utf-8',
            },
            method: 'POST',
            cache: 'no-cache',
            credentials: 'same-origin',
            body: password,
        })
    }
})
$('.delete-password').click(event => {
    fetch('delete_password/', {
        headers: {
            'Content-Type': 'text/plain; charset=utf-8',
        },
        method: 'POST',
        cache: 'no-cache',
        credentials: 'same-origin',
    })
})

$('.code-toggle').click(event => {
    const button = $(event.currentTarget)
    const target = button.parent().children('.panel-block.code')
    target.slideToggle()
})


$('.send-command').click(event => {
    const button = $(event.target)
    const value_source = button.parent().find('[data-value-source]')
    const section_name = button.attr('data-section-name')
    const command_id = button.attr('data-command-id')

    button.addClass('is-loading').removeClass('is-danger')
    value_source.removeClass('is-danger')
    button.closest('.column').find('.error-message').empty()

    let value
    if (value_source.attr('type') === 'checkbox') {
        value = value_source.is(':checked')
    }
    else if (value_source.hasClass('select')) {
        value = value_source.find(':selected').val()
    }
    // type == 'none'
    else if (value_source.length === 0) {
        value = null
    }
    else {
        value = value_source.val()
    }

    fetch('api/', {
        headers: {
            'Content-Type': 'application/json',
        },
        method: 'POST',
        cache: 'no-cache',
        credentials: 'same-origin',
        body: JSON.stringify({
            section_name,
            command_id,
            input: value,
        })
    })
    .then(response => {
        if (response.ok) {
            return response.json()
        }
        throw new Error('A server error occured')
    })
    .then(json => {
        if (json.error) {
            throw new Error(json.error)
        }
        button.removeClass('is-loading')
    })
    .catch(error => {
        console.error(error)
        button.closest('.column').find('.error-message').text(`${error.message}.`)
        button.removeClass('is-loading').addClass('is-danger')
        value_source.addClass('is-danger')
    })

    return false
})
