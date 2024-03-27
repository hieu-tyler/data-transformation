
const StudentTable = ({students, onEdit, onDelete}) => {

  return (
    <div>
      <h1>Student Data</h1>
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Birthdate</th>
            <th>Score</th>
            <th>Grade</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {students.map((student) => (
            <tr key={student.pk}>
              <td>{student.name}</td>
              <td>{student.birthdate}</td>
              <td>{student.score}</td>
              <td>{student.grade}</td>
              <td>
                <button onClick={() => onEdit(student)}>Edit</button>
                <button onClick={() => onDelete(student.pk)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default StudentTable;
