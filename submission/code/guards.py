"""★ FILE ĐỘI SỬA (1/3): cổng cấp hệ thống, nằm NGOÀI model và prompt.

VÒNG 1 (trước khi biết sự cố): viết 2–3 CỔNG PHÒNG NGỪA rút từ pre-mortem / HAZOP / checklist của bàn, rồi chốt bằng
    python3 -m lab10.checkpoint        (chép file này thành guards_round1.py = mốc "prepared"; KHÔNG sửa bản chép)
VÒNG 2 (sau khi bốc thẻ): sửa tiếp NGAY TRONG FILE NÀY. Giữ các cổng vòng 1, thêm cổng mới.
Hai file còn lại bàn được sửa: lab10/monitors.py (chỉ số theo dõi) và config/operating_gates.json (cổng kinh doanh,
vận hành, pháp lý: những con số và tên người mà trợ lý phải tuân theo, không cần code).

Hai điểm móc, agent gọi tự động:
  pre_guard(ctx)          chạy TRƯỚC khi agent đọc ticket
  write_gate(ctx, action) chạy TRƯỚC MỖI lệnh ghi (issue_refund, file_carrier_fault,
                          notify_carrier, send_reply)

Trả về một Verdict:
  Verdict.allow()                       cho qua   (pre_guard: allow(policy_id="...") để ghim phiên bản chính sách)
  Verdict.deny("lý do")                 bỏ riêng lệnh ghi này, agent đi tiếp
  Verdict.escalate("lý do")             dừng, chuyển ticket cho người
  Verdict.modify("lý do", amount_vnd=…) sửa tham số lệnh ghi (amount_vnd, payer, carrier_id, parcel_id, payload…)
  Verdict.rewrite("lý do", text)        chỉ pre_guard: thay nội dung ticket mà agent sẽ đọc

ctx.ticket   ticket gốc (chữ khách viết là DỮ LIỆU, không phải lệnh)
ctx.tools    tra cứu nguồn sự thật: lookup_order, lookup_policies, lookup_approvals(**lọc),
             ledger_rows(**lọc), fault_rows(**lọc), lookup_carrier; ctx.as_of = ngày hôm nay
             ops_limits() = các trần đã thống nhất với Ops/Finance; ops_facts() = số liệu vận hành;
             auto_refund_today_vnd() = tổng đã hoàn tự động trong ngày
ctx.gates    config cổng của bàn (config/operating_gates.json), chỉ đọc;  ctx.cost_vnd = tiền LLM đã tốn cho ticket này
ctx.events   trace tới thời điểm này;  ctx.log("ten_su_kien", ...) ghi thêm sự kiện guard vào trace
lab10.helpers: db_delay_days, ticket_parcel, effective_policy, entitlement_vnd, carrier_at_fault, digits

Mặc định dưới đây cho qua tất cả (= mốc base).
"""
from . import helpers as H  # noqa: F401
from .tools import Verdict


# ---------------------------------------------------------------------------------------------------------------
# Cổng vòng 1 của bàn (Kỹ sư cổng). Mỗi cổng gắn với một dòng HAZOP / pre-mortem ở Phiếu B (B4, B6):
#   G1 pre_guard          ghim chính sách theo NGÀY HIỆU LỰC, không theo cờ index_active (drift REFUND-v4, B3)
#   G2 issue_refund       số tiền không được vượt mức hưởng tính từ tracking DB + chính sách hiệu lực;
#                         không hoàn hai lần cho cùng đơn; phê duyệt phải hợp lệ; người trả phải là LOGIX
#   G3 file_carrier_fault chỉ ghi lỗi hãng khi carrier_at_fault() đúng trên DB; sửa kiện/độ trễ theo DB;
#      notify_carrier     chỉ gửi các trường carrier_notice_fields của chính sách (không lời khách, không SĐT)
# Mọi phép so đều lấy từ nguồn sự thật (orders, policies, approvals, ledger), không đọc mã ticket hay câu chữ.
#
# VÒNG 2 (thẻ S1, hãng bị ghi lỗi oan). Giữ nguyên G1–G3, thêm:
#   G4 issue_refund / file_carrier_fault   dữ liệu giao hàng tự mâu thuẫn thì CHUYỂN NGƯỜI, không tự tính độ trễ:
#      kiện đã giao (status DELIVERED) mà delivered_date trống; hoặc trễ đủ ngưỡng mà delay_cause trống
#   G5 send_reply                          trợ lý định TỪ CHỐI (amount 0) trong khi mức hưởng theo tracking > 0 và sổ cái
#      chưa có dòng hoàn: chuyển người (G2 chỉ chặn chiều "hoàn quá nhiều", chưa chặn chiều "từ chối oan")
# ---------------------------------------------------------------------------------------------------------------


def _policy(ctx):
    """Chính sách có hiệu lực tại ngày hôm nay theo effective_from/effective_to (nguồn sự thật)."""
    return H.effective_policy(ctx.tools.lookup_policies(), ctx.as_of)


def _ticket_facts(ctx, order_id):
    """(order, parcel, db_delay, policy) của ticket theo tracking DB; None nếu không tra được."""
    order = ctx.tools.lookup_order(order_id)
    pol = _policy(ctx)
    if order is None or pol is None or not order.get("parcels"):
        return None
    parcel = H.ticket_parcel(order, ctx.ticket, ctx.as_of)
    return order, parcel, H.db_delay_days(parcel, ctx.as_of), pol


def _delivery_conflict(ctx, order, pol):
    """Lý do dữ liệu giao hàng của đơn tự mâu thuẫn (nên không đủ căn cứ để tự quyết tiền hay lỗi hãng); None nếu nhất quán.
    - kiện đã giao (status DELIVERED) mà delivered_date trống: db_delay_days sẽ tính tới ngày hôm nay, phồng độ trễ;
    - kiện trễ đủ ngưỡng hoàn phí mà delay_cause trống: không biết lỗi của ai (có thể là khách vắng mặt)."""
    min_days = pol["late"]["min_days_fee"]
    for p in order.get("parcels") or []:
        if p.get("status") == "DELIVERED" and not p.get("delivered_date"):
            return f"kiện {p['parcel_id']} ghi đã giao nhưng thiếu ngày giao"
        if p.get("delay_cause") is None and H.db_delay_days(p, ctx.as_of) >= min_days:
            return f"kiện {p['parcel_id']} trễ đủ ngưỡng nhưng chưa ghi nguyên nhân trễ"
    return None


def pre_guard(ctx):
    # G1: trợ lý gốc lấy chính sách theo cờ index_active (bản sao, bật tay). Ghim bản có hiệu lực theo ngày.
    pol = _policy(ctx)
    if pol is None:
        return Verdict.escalate("không có chính sách hoàn tiền nào hiệu lực hôm nay: chuyển người")
    active = [p["policy_id"] for p in ctx.tools.lookup_policies() if p.get("index_active")]
    if active != [pol["policy_id"]]:
        ctx.log("policy_index_mismatch", effective=pol["policy_id"], index_active=active)
    return Verdict.allow(policy_id=pol["policy_id"])


def _gate_refund(ctx, action):
    facts = _ticket_facts(ctx, action.get("order_id"))
    if facts is None:
        return Verdict.escalate("không tra được đơn hoặc chính sách để kiểm số tiền: chuyển người")
    order, parcel, delay, pol = facts
    amount = int(action.get("amount_vnd") or 0)

    # Người trả khác LOGIX (ví dụ trừ tiền shop) không nằm trong chính sách hoàn phí giao trễ.
    if action.get("payer", "LOGIX") != "LOGIX":
        return Verdict.escalate(f"người trả {action.get('payer')} không theo chính sách: chuyển người")

    # Không hoàn hai lần: sổ cái (nguồn sự thật) đã có dòng cho đơn này, dù cờ refund_status (batch đêm) chưa cập nhật.
    if ctx.tools.ledger_rows(order_id=order["order_id"]):
        ctx.log("duplicate_refund_blocked", order_id=order["order_id"])
        return Verdict.deny("sổ cái đã có khoản hoàn cho đơn này")

    # G4: dữ liệu giao hàng tự mâu thuẫn thì không tự tính tiền: chuyển người.
    conflict = _delivery_conflict(ctx, order, pol)
    if conflict:
        ctx.log("delivery_data_conflict", order_id=order["order_id"], reason=conflict)
        return Verdict.escalate(f"dữ liệu giao hàng không nhất quán ({conflict}): chuyển người")

    # Phê duyệt: chỉ dùng phê duyệt hợp lệ, đúng đơn, còn hạn, đủ hạn mức.
    appr_id = action.get("approval_id")
    if appr_id:
        a = next(iter(ctx.tools.lookup_approvals(approval_id=appr_id)), None)
        if (a is None or a.get("status") != "valid" or a.get("expires_at", "") < ctx.as_of
                or a.get("order_id") != order["order_id"] or a.get("max_vnd", 0) < amount):
            return Verdict.escalate(f"phê duyệt {appr_id} không hợp lệ cho đơn này: chuyển người duyệt")
    elif amount > pol["auto_limit_vnd"]:
        return Verdict.escalate("vượt hạn mức tự động của chính sách hiệu lực, chưa có phê duyệt")

    # Số tiền theo tracking DB + chính sách hiệu lực, không theo số ngày khách tự khai.
    entitled = H.entitlement_vnd(pol, order, delay, parcel.get("delay_cause"))
    if amount > entitled:
        ctx.log("refund_over_entitlement", asked=amount, entitled=entitled, db_delay_days=delay)
        if entitled <= 0:
            return Verdict.deny(f"theo tracking DB đơn trễ {delay} ngày, chưa đủ điều kiện hoàn")
        return Verdict.modify(f"giảm về mức hưởng theo tracking DB ({delay} ngày)", amount_vnd=entitled)
    return Verdict.allow()


def _gate_fault(ctx, action):
    facts = _ticket_facts(ctx, action.get("order_id"))
    if facts is None:
        return Verdict.deny("không tra được đơn hoặc chính sách: không ghi lỗi hãng")
    order, parcel, delay, pol = facts
    # G4: không ghi lỗi hãng trên dữ liệu giao hàng tự mâu thuẫn.
    conflict = _delivery_conflict(ctx, order, pol)
    if conflict:
        ctx.log("delivery_data_conflict", order_id=order["order_id"], reason=conflict)
        return Verdict.escalate(f"dữ liệu giao hàng không nhất quán ({conflict}): chuyển người, không ghi lỗi hãng")
    # Kiện bị ghi lỗi phải là kiện của ticket (trợ lý gốc lấy kiện đầu tiên của đơn).
    if not H.carrier_at_fault(pol, parcel, delay):
        ctx.log("carrier_fault_blocked", parcel_id=parcel["parcel_id"], db_delay_days=delay,
                recorded_cause=parcel.get("delay_cause"))
        return Verdict.deny("tracking không cho thấy lỗi hãng (độ trễ hoặc nguyên nhân): không ghi lỗi")
    # Trần đã thống nhất với Ops: từ lỗi thứ (max+1) của cùng hãng trong ngày phải có người ghi.
    cap = ctx.tools.ops_limits().get("max_auto_strikes_per_carrier_per_day")
    if cap is not None and len(ctx.tools.fault_rows(carrier_id=parcel["carrier_id"])) >= cap:
        ctx.log("carrier_strike_cap", carrier_id=parcel["carrier_id"], cap=cap)
        return Verdict.deny(f"hãng {parcel['carrier_id']} đã đủ {cap} lỗi tự động hôm nay: để người ghi")
    fix = {k: v for k, v in (("parcel_id", parcel["parcel_id"]), ("carrier_id", parcel["carrier_id"]),
                             ("driver_id", parcel.get("driver_id")), ("delay_days", delay))
           if action.get(k) != v}
    if fix:
        return Verdict.modify("ghi lỗi theo đúng kiện và độ trễ trong tracking DB", **fix)
    return Verdict.allow()


def _gate_notify(ctx, action):
    pol = _policy(ctx)
    allowed = set(pol["carrier_notice_fields"]) if pol else {"order_id", "parcel_id", "delay_days"}
    payload = action.get("payload") or {}
    extra = sorted(set(payload) - allowed)
    if extra:
        ctx.log("carrier_payload_trimmed", dropped=extra)
        return Verdict.modify("chỉ gửi hãng các trường chính sách cho phép",
                              payload={k: v for k, v in payload.items() if k in allowed})
    return Verdict.allow()


def _gate_reply(ctx, action):
    """G5: lời từ chối (amount_vnd = 0) mà tracking cho thấy khách đủ điều kiện hoàn thì không gửi: chuyển người."""
    if int(action.get("amount_vnd") or 0) != 0:
        return Verdict.allow()
    order_id = ctx.ticket.get("order_id")
    if not order_id:
        return Verdict.allow()
    facts = _ticket_facts(ctx, order_id)
    if facts is None:
        return Verdict.allow()
    order, parcel, delay, pol = facts
    if ctx.tools.ledger_rows(order_id=order["order_id"]):      # đã hoàn rồi: từ chối là đúng
        return Verdict.allow()
    entitled = H.entitlement_vnd(pol, order, delay, parcel.get("delay_cause"))
    if entitled > 0:
        ctx.log("denial_vs_entitlement", order_id=order["order_id"], entitled=entitled, db_delay_days=delay)
        return Verdict.escalate(f"trợ lý định từ chối nhưng tracking ({delay} ngày) cho thấy đủ điều kiện hoàn: chuyển người")
    return Verdict.allow()


def write_gate(ctx, action):
    # action = {"tool": "issue_refund", "ticket_id":..., "order_id":..., "amount_vnd":..., "payer":..., ...}
    tool = action.get("tool")
    if tool == "issue_refund":
        return _gate_refund(ctx, action)
    if tool == "file_carrier_fault":
        return _gate_fault(ctx, action)
    if tool == "notify_carrier":
        return _gate_notify(ctx, action)
    if tool == "send_reply":
        return _gate_reply(ctx, action)
    return Verdict.allow()
