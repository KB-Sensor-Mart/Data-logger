readJsonFile('./data.json')
  .then((data) => {
    console.log('Data read from file:', data);
  })
  .catch((error) => {
    console.error('Error reading file:', error);
  });