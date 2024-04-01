import './App.css';
import UploadForm from './UploadForm';
import StudentTable from './StudentTable';

import React, { useState, useMemo, useEffect } from 'react';

function App() {
	const [students, setStudents] = useState([]);

	const fetchData = async () => {
		try {
			const response = await fetch('http://localhost:8000/api/student/');
			if (!response.ok) {
				throw new Error('Failed to fetch data');
			}
			const data = await response.json();
			setStudents(data);
		} catch (error) {
			console.error('Error fetching data:', error);
		}
	};

	useEffect(() => {

		fetchData();
	}, []);

	const memoizedStudents = useMemo(() => students, [students]);

	const handleEdit = async (student) => {
		// Add your logic to handle editing a student record
		console.log('Editing student:', student);
		try {
			const response = await fetch(`http://localhost:8000/api/student/${student.pk}`,
				{
					method: 'PUT',
					body: {
						'name': student.name,
						'birthdate': student.birthdate,
						'score': student.score,
						'grade': student.grade,
					},
				})
			if (!response.ok) {
				throw new Error('Failed to edit student');
			} else {
				fetchData();
			}
		} catch (error) {
			console.error('Error editing student', error)
		}
	};

	const handleDelete = async (studentId) => {
		try {
			const response = await fetch(`http://localhost:8000/api/student/${studentId}`, {
				method: 'DELETE',
			});
			if (!response.ok) {
				throw new Error('Failed to delete student');
			} else {
				fetchData();
			}

		} catch (error) {
			console.error('Error deleting student:', error);
		}
	};

	const handleUploadSuccess = async () => {
		fetchData(); 
	  };

	return (
		<div className="App">
			<h1>Student Data App</h1>
			<main>
				<StudentTable students={memoizedStudents} onEdit={handleEdit} onDelete={handleDelete}/>
				<UploadForm onUploadSuccess={handleUploadSuccess}/>
			</main>
		</div>
	);
}

export default App;
