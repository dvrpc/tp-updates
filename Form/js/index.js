const addForm = document.getElementById('add-indicator')
const removeForm = document.getElementById('remove-indicator')


// Handle form data
const makeOptions = (method, body) => {
    return {
        method,
        mode: 'cors',
        header: {
            'Content-Type': 'applications/json',
            'Accept': 'applications/json'
        },
        body: JSON.stringify(body)
    }
}
const addIndicator = async body => {
    const options = makeOptions('POST', body)

    try {
        const stream = await fetch('http://linux2.dvrpc.org/tracking-progress/v1/indicators/', options)
        if(stream.ok) alert('Indicator successfully added to update list.')
    }catch(error) {
        alert('Failed to add indicator due to: ', error)
    }
}
const removeIndicator = async body => {
    const options = makeOptions('DELETE', body)

    try {
        const stream = await fetch('http://linux2.dvrpc.org/tracking-progress/v1/indicators/', options)
        if(stream.ok) alert('Indicator successfully removed from update list.')
    }catch(error) {
        alert('Failed to remove indicator due to: ', error)
    }
}
const getFormData = e => {
    let data = {}

    // extract all the information from the form as a FormData object
    let formData = new FormData(e.target)

    // Iterate over the key/value pairs created by the form data object.
    for(var [key, value] of formData.entries()) {
        let safeValue = value.trim().split('-').join(' ')
        data["name"] = safeValue
    }

    return data
}


// Handle Form Submission
addForm.onsubmit = e => {
    e.preventDefault()
    const indicator = getFormData(e)
    addIndicator(indicator)
}
removeForm.onsubmit = e => {
    e.preventDefault()
    const indicator = getFormData(e)
    removeIndicator(indicator)
}
