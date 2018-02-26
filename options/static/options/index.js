import commandConfig from './commands.js'


$(".send-command").click(event => {
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
})
