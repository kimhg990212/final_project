import { useEffect, useState } from "react";
import "../css/AdminPage.css";

function AdminPage() {
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [searchNickname, setSearchNickname] = useState("");
  const [currentPage, setCurrentPage] = useState(1);

  const [adminInfo, setAdminInfo] = useState(null);
  const [trademarks, setTrademarks] = useState([]);
  const [trademarkKeyword, setTrademarkKeyword] = useState("");
  const [trademarkPage, setTrademarkPage] = useState(1);
  const [trademarkTotal, setTrademarkTotal] = useState(0);

  const API_BASE_URL = "http://localhost:5000";
  const USERS_PER_PAGE = 10;
  const TRADEMARKS_PER_PAGE = 12;

  useEffect(() => {
    fetch(`${API_BASE_URL}/admin/users`)
      .then((res) => res.json())
      .then((data) => setUsers(data))
      .catch((err) => console.error("유저 목록 조회 실패:", err));
  }, []);

  useEffect(() => {
    const savedUser = JSON.parse(localStorage.getItem("user"));

    if (savedUser) {
      setAdminInfo(savedUser);
    }
  }, []);

  useEffect(() => {
    fetch(
      `${API_BASE_URL}/admin/trademarks?page=${trademarkPage}&size=${TRADEMARKS_PER_PAGE}&keyword=${trademarkKeyword}`,
    )
      .then((res) => res.json())
      .then((data) => {
        setTrademarks(data.items || []);
        setTrademarkTotal(data.total || 0);
      })
      .catch((err) => console.error("상표 목록 조회 실패:", err));
  }, [trademarkPage, trademarkKeyword]);

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

  const trademarkTotalPages = Math.ceil(trademarkTotal / TRADEMARKS_PER_PAGE);

  const handleTrademarkSearch = (e) => {
    setTrademarkKeyword(e.target.value);
    setTrademarkPage(1);
  };

  const handleDeleteTrademark = async (trademarkId) => {
    if (!window.confirm("정말 이 상표를 삭제하시겠습니까?")) {
      return;
    }

    try {
      const res = await fetch(
        `${API_BASE_URL}/admin/trademarks/${trademarkId}`,
        {
          method: "DELETE",
        },
      );

      if (!res.ok) {
        throw new Error("상표 삭제 실패");
      }

      alert("상표가 삭제되었습니다.");

      setTrademarks((prev) => prev.filter((item) => item.id !== trademarkId));

      setTrademarkTotal((prev) => prev - 1);
    } catch (err) {
      console.error(err);
      alert("상표 삭제 중 오류가 발생했습니다.");
    }
  };

  return (
    <div className="admin-page">
      <h1>관리자 대시보드</h1>

      <section className="admin-card">
        <h2>현재 관리자 정보</h2>

        {adminInfo ? (
          <>
            <p>닉네임: {adminInfo.nickname}</p>
            <p>이메일: {adminInfo.email}</p>
          </>
        ) : (
          <p>관리자 정보를 불러올 수 없습니다.</p>
        )}
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

      <section className="admin-card">
        <div className="admin-section-header">
          <div>
            <h2>전체 상표 목록</h2>
            <p>총 {trademarkTotal.toLocaleString()}개 결과</p>
          </div>

          <input
            type="text"
            placeholder="상표명, 출원인 검색"
            value={trademarkKeyword}
            onChange={handleTrademarkSearch}
            className="admin-search-input"
          />
        </div>

        <div className="admin-trademark-grid">
          {trademarks.map((item) => (
            <div className="admin-trademark-card" key={item.id}>
              <div className="admin-trademark-image">
                {item.image_url ? (
                  <img src={item.image_url} alt={item.title || "상표 이미지"} />
                ) : (
                  <span>이미지 없음</span>
                )}
              </div>

              <div className="admin-trademark-info">
                <strong>{item.title || "(상표명 없음)"}</strong>
                <p>{item.applicant_name || "출원인 없음"}</p>
                <span>{item.application_date}</span>
              </div>

              <button
                type="button"
                className="admin-delete-btn"
                onClick={() => handleDeleteTrademark(item.id)}
              >
                삭제
              </button>
            </div>
          ))}
        </div>

        <div className="admin-pagination">
          <button
            disabled={trademarkPage === 1}
            onClick={() => setTrademarkPage(trademarkPage - 1)}
          >
            이전
          </button>

          <span>
            {trademarkPage} / {trademarkTotalPages || 1}
          </span>

          <button
            disabled={
              trademarkPage === trademarkTotalPages || trademarkTotalPages === 0
            }
            onClick={() => setTrademarkPage(trademarkPage + 1)}
          >
            다음
          </button>
        </div>
      </section>
    </div>
  );
}

export default AdminPage;
