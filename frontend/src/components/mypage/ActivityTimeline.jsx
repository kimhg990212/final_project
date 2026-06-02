const tabLabels = {
  all: "전체",
  search: "검색",
  create: "생성",
  download: "다운로드",
};

function ActivityTimeline({
  activeTab,
  onTabChange,
  items,
  stats,
  onDownload,
  disabled = false,
}) {
  return (
    <section className="mypage-card timeline-card">
      <div className="section-heading">
        <span className="section-kicker">활동 이력</span>
        <h2>최근 활동</h2>
      </div>

      <div className="timeline-tabs" role="tablist" aria-label="활동 이력 필터">
        {Object.entries(tabLabels).map(([key, label]) => (
          <button
            key={key}
            type="button"
            className={activeTab === key ? "tab-button active" : "tab-button"}
            onClick={() => onTabChange(key)}
            disabled={disabled}
          >
            {label}
            <span>{stats[key]}</span>
          </button>
        ))}
      </div>

      <div className="timeline-list">
        {items.length === 0 ? (
          <div className="timeline-empty">선택한 필터의 활동이 없습니다.</div>
        ) : (
          items.map((item) => (
            <article key={item.id} className="timeline-item">
              <div className={`timeline-badge ${item.type}`}>
                {tabLabels[item.type]}
              </div>

              <div className="timeline-content">
                <div className="timeline-title-row">
                  <h3>{item.title}</h3>
                  <span>{item.time}</span>
                </div>
                <p>{item.description}</p>
              </div>

              <div className="timeline-actions">
                <button
                  type="button"
                  className="ghost-action"
                  onClick={() => onDownload(item)}
                  disabled={disabled || !item.canDownload}
                >
                  다운로드
                </button>
              </div>
            </article>
          ))
        )}
      </div>
    </section>
  );
}

export default ActivityTimeline;
