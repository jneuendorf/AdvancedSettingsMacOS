import commandConfig from './commands.js'


$(".send-command").click(event => {
    const button = $(event.target)
    button.addClass('is-loading')

    const value_source = button.parent().find('[data-value-source]')
    const section_name = button.attr('data-section-name')
    const command_id = button.attr('data-command-id')

    let value
    if (value_source.attr('type') === 'checkbox') {
        value = value_source.is(':checked')
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
    .then(response => response.json())
    .then(json => {

        button.removeClass('is-loading')
    })
    .catch(error => {
        console.error(error)
        button.removeClass('is-loading')
    })
})
