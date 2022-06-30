const activeList = document.getElementById('active-indicators')
const addForm = document.getElementById('add-indicator')
const removeForm = document.getElementById('remove-indicator')

// Create list of active jawns
const populateList = async list => {
    const stream = await fetch('http://linux2.dvrpc.org/tracking-progress/v1/indicators')

    try {
        if(stream.ok) {
            // purge before updating
            while(activeList.firstChild) activeList.removeChild(activeList.firstChild)

            const data = await stream.json()
            const frag = document.createDocumentFragment()
            
            if(data.length) {
                data.forEach(indicator => {
                    const li = document.createElement('li')
                    li.textContent = indicator.split('-').join(' ')
                    frag.appendChild(li)
                })
            } else {
                const li = document.createElement('li')
                li.textContent = 'There are currently no recently updated indicators'
                li.classList.add('empty-list-item')
                frag.appendChild(li)
            }
            
            list.appendChild(frag)

            return true
        }
    } catch(error) {
        return false
    }
}

// Handle form data
const makeOptions = (method, body) => {
    return {
        method,
        mode: 'cors',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        body: JSON.stringify(body)
    }
}

const addIndicator = async body => {
    const options = makeOptions('POST', body)

    try {
        const stream = await fetch('http://linux2.dvrpc.org/tracking-progress/v1/indicators', options)

        if(stream.ok) {
            return true
        }
        else {
            return false
        }

    }catch(error) {
        return false
    }
}

const removeIndicator = async body => {
    const options = makeOptions('DELETE', body)

    try {
        const stream = await fetch('http://linux2.dvrpc.org/tracking-progress/v1/indicators', options)
        
        if(stream.ok) {
            return true
        }
        else {
            alert('Failed to remove indicator due to LASAGNA OVERLOAD')
            return false
        }

    }catch(error) {
        alert('Failed to remove indicator due to: ', error)
        return false
    }
}

const getFormData = e => {
    let data = {}

    let formData = new FormData(e.target)

    for(var [key, value] of formData.entries()) {
        let safeValue = value.trim()
        data["name"] = safeValue
    }

    return data
}


// Handle Form Submission
addForm.onsubmit = async e => {
    e.preventDefault()

    const indicator = getFormData(e)
    const success = await addIndicator(indicator)

    if(success) {
        await populateList(activeList)
        alert(`Success! Added ${indicator.name.split('-').join(' ')} to the updates list.`)
    }
}

removeForm.onsubmit = async e => {
    e.preventDefault()

    const indicator = getFormData(e)
    const success = await removeIndicator(indicator)

    if(success) {
        await populateList(activeList)
        alert(`${indicator.name.split('-').join(' ')} indicator removed from update list.`)
    }
}

populateList(activeList)