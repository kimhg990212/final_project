import { useEffect, useState } from "react";
import "../css/AdminPage.css";

function AdminPage() {
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [searchNickname, setSearchNickname] = useState("");
  const [currentPage, setCurrentPage] = useState(1);

  const API_BASE_URL = "http://localhost:5000";
  const USERS_PER_PAGE = 10;

  useEffect(() => {
    fetch(`${API_BASE_URL}/admin/users`)
      .then((res) => res.json())
      .then((data) => setUsers(data))
      .catch((err) => console.error("유저 목록 조회 실패:", err));
  }, []);

  const handleUserDetail = async (userId) => {
    const res = await fetch(`${API_BASE_URL}/admin/users/${userId}`);
    const data = await res.json();
    setSelectedUser(data);
  };

  const filteredUsers = users.filter((user) =>
    user.nickname?.toLowerCase().includes(searchNickname.toLowerCase()),
  );

  const totalPages = Math.ceil(filteredUsers.length / USERS_PER_PAGE);
  const startIndex = (currentPage - 1) * USERS_PER_PAGE;
  const currentUsers = filteredUsers.slice(
    startIndex,
    startIndex + USERS_PER_PAGE,
  );

  const handleSearchChange = (e) => {
    setSearchNickname(e.target.value);
    setCurrentPage(1);
  };

  return (
    <div className="admin-page">
      <h1>관리자 대시보드</h1>

      <section className="admin-card">
        <h2>현재 관리자 정보</h2>
        <p>닉네임: 관리자</p>
        <p>이메일: test@test.com</p>
      </section>

      <section className="admin-card">
        <div className="admin-section-header">
          <h2>유저 목록</h2>
          <input
            type="text"
            placeholder="닉네임 검색"
            value={searchNickname}
            onChange={handleSearchChange}
            className="admin-search-input"
          />
        </div>

        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>이메일</th>
              <th>닉네임</th>
              <th>권한</th>
              <th>상세</th>
            </tr>
          </thead>

          <tbody>
            {currentUsers.map((user) => (
              <tr key={user.id}>
                <td>{user.id}</td>
                <td>{user.email}</td>
                <td>{user.nickname}</td>
                <td>{user.role}</td>
                <td>
                  <button onClick={() => handleUserDetail(user.id)}>
                    보기
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        <div className="admin-pagination">
          <button
            disabled={currentPage === 1}
            onClick={() => setCurrentPage(currentPage - 1)}
          >
            이전
          </button>

          <span>
            {currentPage} / {totalPages || 1}
          </span>

          <button
            disabled={currentPage === totalPages || totalPages === 0}
            onClick={() => setCurrentPage(currentPage + 1)}
          >
            다음
          </button>
        </div>
      </section>

      {selectedUser && (
        <section className="admin-card">
          <h2>유저 상세 정보</h2>
          <p>ID: {selectedUser.id}</p>
          <p>이메일: {selectedUser.email}</p>
          <p>닉네임: {selectedUser.nickname}</p>
          <p>권한: {selectedUser.role}</p>
        </section>
      )}
    </div>
  );
}

export default AdminPage;
