import axios from axios;


async function fetchData() {
    try {
        const response = await axios.get('http://localhost:5000');
        const data = response.data;
        console.log(data);  // Process the data as needed
    } catch (error) {
        console.error('Error fetching data from Python API:', error);
    }
}

// Call the fetchData function as needed
fetchData();

