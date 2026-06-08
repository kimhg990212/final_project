import axios from "axios";

const API_BASE_URL = "http://localhost:5000";

export const getAdminTrademarks = async ({
  page = 1,
  size = 12,
  keyword = "",
  sort = "latest",
}) => {
  const res = await axios.get(`${API_BASE_URL}/admin/trademarks`, {
    params: { page, size, keyword, sort },
  });

  return res.data;
};
