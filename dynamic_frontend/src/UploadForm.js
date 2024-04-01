// UploadForm.js

import React, { useState } from 'react';

const UploadForm = ({onUploadSuccess}) => {
  const [file, setFile] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/api/upload/', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        alert('File uploaded successfully!');
        onUploadSuccess();
      } else {
        const data = await response.json();
        alert('Failed to upload file: ' + data.error);
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      alert('An error occurred while uploading the file.');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input type="file" accept=".csv,.xlsx,.xls" onChange={handleFileChange} />
      <button type="submit">Upload</button>
    </form>
  );
};

export default UploadForm;
