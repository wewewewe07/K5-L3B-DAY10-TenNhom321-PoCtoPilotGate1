"""★ FILE ĐỘI SỬA (2/3): chỉ số theo dõi (monitor). Thêm ÍT NHẤT MỘT chỉ số bắt được sự cố của bàn.

Mỗi monitor nhận danh sách trial (KHÔNG có nhãn đúng/sai, giống production) và trả về một số.
Một trial = {"ticket_id", "seed", "day", "status", "amount_vnd", "ticket", "events", "ledger", "faults", "outbound",
             "arrive_min", "warehouse", "cost_vnd", "review_kind", "queue_wait_min", "queue_stuck"}
  "day"            một ngày vận hành giả lập: các ticket cùng "day" và cùng "seed" chạy nối nhau trên cùng một sổ cái
  "arrive_min"     phút ticket tới trong ca (0..480)          "warehouse"   kho của đơn
  "cost_vnd"       tiền LLM + nền tảng đã tốn cho ticket      "review_kind" None / "escalated" (trợ lý chuyển người) /
  "queue_wait_min" số phút chờ người duyệt (None nếu không vào hàng chờ)     "recheck" (nhân viên tự kiểm lại)
Chỉ số có thể là kỹ thuật (tỉ lệ model đè số trong ticket lên DB), vận hành (số ca cần người trong giờ đông nhất),
hay kinh doanh (tỉ lệ ticket trợ lý đọc xong vẫn phải chuyển người).

lab10.grade kiểm: monitor chạy không lỗi, và giá trị trên gói sự cố khác giá trị trên bộ nền,
tức là monitor "sáng đèn" khi sự cố xảy ra.
"""


def escalation_rate(trials):
    return sum(t["status"] == "escalated" for t in trials) / max(1, len(trials))


# ---- Chỉ số của bàn cho thẻ S1 (hãng bị ghi lỗi oan) ----------------------------------------------------------------
def claim_vs_db_mismatch_rate(trials):
    """Tỉ lệ ticket mà số ngày trễ khách khai KHÁC tracking và trợ lý để số khách đè lên DB (sự kiện model_override).
    Lệch cả hai chiều (khai cao: hoàn và ghi lỗi oan; khai thấp: từ chối oan). Kỹ thuật: bắt nhánh [1] của fault tree."""
    hit = sum(any(e.get("type") == "model_override" and e.get("ticket") != e.get("db") for e in t["events"]) for t in trials)
    return round(hit / max(1, len(trials)), 4)


def delivery_data_conflict_rate(trials):
    """Tỉ lệ ticket có dữ liệu giao hàng không đủ để quyết: trễ mà chưa ghi nguyên nhân (cause_recorded = false), hoặc cổng G4
    đã chặn vì kiện đã giao nhưng thiếu ngày giao (sự kiện delivery_data_conflict). Dữ liệu (nhánh [2], [3])."""
    def bad(t):
        return any(e.get("type") == "delivery_data_conflict"
                   or (e.get("type") == "tracking" and e.get("cause_recorded") is False and e.get("db_delay_days", 0) > 0)
                   for e in t["events"])
    return round(sum(bad(t) for t in trials) / max(1, len(trials)), 4)


def max_faults_per_carrier_day(trials):
    """Số lỗi giao trễ nhiều nhất đã ghi cho MỘT hãng trong MỘT ngày vận hành (gộp mọi ticket cùng seed và cùng day).
    Trần Ops là 2; ngưỡng ngưng tuyến của hãng là 3 lỗi trong 7 ngày. Vận hành, nhánh [4]; mức 3 trở lên là đèn đỏ."""
    seen, per = set(), {}
    for t in trials:
        for f in t["faults"]:
            key = (t["seed"], t["day"], f.get("ticket_id"), f.get("parcel_id"), f["carrier_id"])
            if key in seen:
                continue
            seen.add(key)
            k = (t["seed"], t["day"], f["carrier_id"])
            per[k] = per.get(k, 0) + 1
    return max(per.values(), default=0)


MONITORS = {
    "escalation_rate": escalation_rate,     # có sẵn; KHÔNG tính là metric mới của đội
    "claim_vs_db_mismatch_rate": claim_vs_db_mismatch_rate,
    "delivery_data_conflict_rate": delivery_data_conflict_rate,
    "max_faults_per_carrier_day": max_faults_per_carrier_day,
}
STARTER_MONITORS = ("escalation_rate",)
