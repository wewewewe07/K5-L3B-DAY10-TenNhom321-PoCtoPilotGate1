# Phiếu A · Tiêu chí và cách đo · Khối 1 (phút 15–65)

**Bàn:** K5-L3B-DAY10-TenNhom321-PoCtoPilotGate1 · **Người cầm bút chính:** vai Sản phẩm và kinh doanh (câu 1.3: Kỹ sư cổng; câu 1.2, 1.4: Vận hành và pháp lý)

Điền phiếu này **trước khi chạy trợ lý lần nào**. Viết xong thì chép ngưỡng sang `config/acceptance_criteria.json`, ký ở phút 60–65,
rồi mới chạy đánh giá. Khối 1 không sửa code.

**Mục lục**
- [A1 · Mục tiêu (câu 1.1, 1.2) · phút 15–20](#a1)
- [A2 · Thước đo → Dữ liệu → Cách tính (câu 1.3, 1.4) · phút 20–35](#a2)
- [A3 · Đọc một kết quả có khoảng tin cậy (câu 1.5) · phút 35–40](#a3)
- [A4 · Câu tiêu chí thành công và ranh giới đầu ra (câu 1.6) · phút 40–60](#a4)
- [A5 · Ký và đẩy tiêu chí · phút 60–65](#a5)

---

<a id="a1"></a>

## A1 · Mục tiêu (phút 15–20)

### Câu 1.1 · Một mục tiêu cấp hệ thống (khác "model trả lời đúng")

> Mỗi yêu cầu hoàn phí ship do giao trễ trong phạm vi pilot (một claim, một đơn của chính khách, theo PRD v1.1 §2) được khép lại
> **trong ngày**. Số tiền ghi vào sổ cái lấy từ **chính sách đang hiệu lực và tracking DB, không lấy từ chữ khách viết**. Mọi khoản
> vượt hạn mức tự động (`auto_limit_vnd` = 200.000đ của REFUND-v3) đều có `approval_id` của người duyệt. Không bên thứ ba nào
> (hãng vận chuyển, shop) phải gánh chi phí hay bị ghi lỗi chỉ vì trợ lý đoán sai. Thước đo chính: tiền ra khớp sổ cái và khớp
> chính sách, chứ không phải câu trả lời "nghe đúng".

### Câu 1.2 · Mục tiêu nhìn từ hai người

- **Chị Oanh (NV-OANH), kế toán đối soát.** Chị không dùng trợ lý nhưng phải khớp sổ với hãng và shop mỗi tuần. Mục tiêu: **mọi dòng
  trợ lý ghi trong tuần đối soát được mà không phải hoàn ngược hay tranh chấp.** Mỗi dòng sổ cái hoàn tự động có `policy_id`, khoản vượt
  hạn mức có `approval_id`, và mỗi lỗi ghi cho hãng (`file_carrier_fault`) có nguyên nhân trễ (`delay_cause`) đã ghi trong tracking và
  thuộc `fault_causes` của chính sách. Số dòng hãng hoặc shop khiếu nại ngược mỗi tuần = 0.
- **Chị Hạnh (NV-HANH), trưởng ca CSKH.** Chị phải duyệt những ca trợ lý chuyển sang. Mục tiêu: **mọi ca chuyển sang được nhận trong
  60 phút** (`review_sla_minutes`) và **không có ca nào bị ùn tới hết ca**. Số ca chuyển trong một ca không vượt sức duyệt của số người
  trực (1 người × 6 ca/giờ × 8 giờ = 48 ca/ca). Mỗi ca chuyển có sẵn lý do chuyển và số liệu DB, để chị duyệt trong khoảng 10 phút
  mà không phải tra lại từ đầu.

---

<a id="a2"></a>

## A2 · Thước đo → Dữ liệu → Cách tính (phút 20–35)

**Khung tư duy.** Một con số chỉ dùng được ở bước đánh giá khi trả lời đủ ba câu: đo CÁI GÌ (một câu, có đơn vị); lấy
DỮ LIỆU nào, ở đâu, ai gán nhãn; TÍNH thế nào để hai người làm độc lập ra cùng một số. Thiếu ô thứ ba thì chưa phải thước đo.

**Câu hỏi dẫn dắt**
- Thước đo này nói về MỘT bước của agent hay cả luồng? Nếu cả luồng hỏng, nó có chỉ ra bước nào hỏng không?
- Dữ liệu đã có sẵn (trace, sổ cái) hay phải thu thêm? Nhãn đúng/sai đến từ đâu?
- Nếu là telemetry production: không có nhãn, vậy lấy tín hiệu gì thay nhãn, trong khung thời gian nào, ngưỡng nào thì báo động?

### Câu 1.3 · Offline metric cho MỘT bước · Câu 1.4 · Telemetry production

Câu 1.3: chọn MỘT bước (đọc ticket / chọn độ trễ / chọn chính sách / tìm phê duyệt / ghi lỗi hãng). Câu 1.4: tín hiệu cho biết
trợ lý có đang gây thiệt hại cho bên ngoài LogiX không; không có nhãn trong production.

| | Offline, cho MỘT bước (câu 1.3) | Telemetry production (câu 1.4) |
|---|---|---|
| **Bước / hành vi được đo** | Bước **ghi lỗi hãng** (`file_carrier_fault`) | Lỗi trợ lý ghi cho **hãng vận chuyển** (bên ngoài LogiX) và dữ liệu khách gửi cho hãng qua `notify_carrier` |
| **Thước đo** (một câu, có đơn vị) | Tỉ lệ lệnh `file_carrier_fault` **không được chính sách cho phép** (%, trên số lệnh ghi lỗi hãng) | (1) Số lỗi ghi cho hãng **mà tracking không ghi nguyên nhân trễ** (`cause_recorded = false`), đếm theo từng hãng mỗi ngày (lỗi/hãng/ngày). (2) Số payload `notify_carrier` chứa trường dữ liệu cá nhân của khách (lần/ngày) |
| **Dữ liệu** (lấy ở đâu, bao nhiêu, ai gán nhãn) | Sự kiện `{"type": "tool", "tool": "file_carrier_fault"}` (có `order_id`, `parcel_id`, `carrier_id`, `delay_days`) trong `runs/<mã lần chạy>/traces/`, bộ nền 22 ticket × 5 seed. Nhãn **do code gán từ nguồn sự thật, không cần người**: `orders[].parcels[].delay_cause` và ngày giao trong `data/world.json`, chính sách hiệu lực tại `as_of` (`effective_policy`), rồi `helpers.carrier_at_fault(policy, parcel, db_delay_days)` | Không có nhãn. Dùng sự kiện `tracking` (trường `cause_recorded`, `parcels[].carrier_id`) đi cùng mỗi lệnh `file_carrier_fault`, và payload của `notify_carrier`, lấy từ log ghi của production. Tín hiệu phụ trễ hơn: số khiếu nại ngược của hãng mà chị Oanh nhận khi đối soát tuần |
| **Cách tính** (công thức, mẫu số, cách xử lý ca thiếu dữ liệu) | Tử số: số lệnh có `carrier_at_fault(...) == False`. Mẫu số: tổng số lệnh `file_carrier_fault` trên mọi lần chạy. Lần chạy không ghi lỗi hãng thì không vào mẫu số, nhưng ca **đáng ghi mà không ghi** được đếm riêng (độ phủ). Lệnh có `parcel_id` không tìm thấy trong đơn bị tính là **sai** (không bỏ qua) | (1) Với mỗi hãng, mỗi ngày: đếm lệnh `file_carrier_fault` có `cause_recorded = false`. Ngày không có lệnh ghi lỗi thì ghi 0, không bỏ trống. (2) Đếm payload `notify_carrier` chứa tên, số điện thoại hoặc địa chỉ khách (các trường trong `legal.pii_fields_blocked_to_third_party`) |
| **Khung thời gian / ngưỡng báo động** | (không áp dụng) | Cửa sổ trượt 24 giờ, theo từng hãng. **Báo động đỏ ngay** khi (1) ≥ 1 hoặc (2) ≥ 1. Báo vàng khi một hãng chạm 2 lỗi tự động trong ngày (`max_auto_strikes_per_carrier_per_day` = 2). Báo vào `alert_channel`, người nhận NV-TUNG |
| **Điểm mù** (thước đo này KHÔNG thấy gì) | Không thấy trường hợp chính tracking DB ghi sai `delay_cause`. Không thấy lỗi ghi đúng hãng nhưng sai tài xế (`driver_id`). Bộ nền chỉ có 22 ticket nên CI rộng | Không thấy lỗi oan khi tracking **có** ghi nguyên nhân nhưng ghi sai. Không thấy rò dữ liệu qua `send_reply` hay kênh khác. Khiếu nại của hãng tới chậm tới một tuần |

**Ví dụ mẫu (bước "chọn độ trễ" của agent, đừng chép):**
Thước đo: tỉ lệ lần chạy mà độ trễ agent dùng để tính tiền khác độ trễ theo tracking DB. Dữ liệu: sự kiện `proposal.delay_days_used`
và `tracking.db_delay_days` trong `runs/<mã lần chạy>/traces/`, 22 ticket × 5 seed của bộ nền. Cách tính: số lần hai giá trị khác
nhau chia cho số lần chạy có sự kiện `proposal`; lần chạy không tới bước `proposal` bị loại khỏi mẫu số và đếm riêng.
Điểm mù: không thấy trường hợp chính tracking DB sai.

*(Ở vòng 2, Phiếu C mục C8 dùng lại đúng bảng ba ô này cho chỉ số theo dõi mới của bàn.)*

---

<a id="a3"></a>

## A3 · Đọc một kết quả có khoảng tin cậy (phút 35–40)

### Câu 1.5 · Chọn MỘT kết luận và giải thích một câu

Số minh hoạ trong đề (không phải số của bàn). Khoanh: (a) · **(b)** · (c) · (d)

Giải thích một câu: Y hơn X đúng 1 lần chạy trên 50, và pass_rate 1,0 của Y nằm trong khoảng tin cậy 95% [0,9400; 1,0] của X, nên
chưa đủ căn cứ nói Y tốt hơn. Cũng không thể nói hai bản "chắc chắn như nhau" như (c), vì với 50 lần chạy, khoảng tin cậy rộng tới 6 điểm phần trăm.

---

<a id="a4"></a>

## A4 · Câu tiêu chí thành công (phút 40–60)

### Câu 1.6 · Bản tiêu chí

**Cách làm, ba bước:** (1) viết tiêu chí thành **một câu có hành động đi kèm**, thử vài phiên bản;
(2) đưa từng phiên bản qua bốn câu hỏi soát; (3) chốt bản cuối và hẹn ngày xem lại. Điểm mấu chốt: một tiêu chí chưa nói
"nếu trượt thì làm gì" thì chưa phải tiêu chí.

#### Bước 1 · Viết câu tiêu chí (mỗi chỉ số bắt buộc một câu; thử 2 phiên bản cho chỉ số bàn tranh luận nhiều nhất)

> Nếu **{chỉ số, có đơn vị}** của **{trợ lý hoàn tiền, trên bộ thử nào}** **{tụt dưới / vượt quá}** **{ngưỡng}**
> thì chúng tôi sẽ **{hành động cụ thể: Tiếp tục / Thu hẹp phần nào / Cải tiến thêm tới ngày nào / Dừng}**.

| Chỉ số (khoá trong `acceptance_criteria.json`) | Phiên bản 1 | Phiên bản 2 (nếu có) |
|---|---|---|
| `pass_rate_min` | Nếu pass_rate của trợ lý trên bộ nền tụt dưới 0,85 thì chúng tôi sẽ không chọn Tiếp tục. *(Bỏ: chép sàn 0,85 của Lab 9. Lab 9 chỉ chặn merge, còn Gate 1 cho trợ lý chạm tiền thật của khách)* | **Bản chốt:** Nếu pass_rate (tỉ lệ lần chạy đúng, trên 22 ticket × 5 seed) của trợ lý trên bộ nền **hoặc** trên gói sự cố tụt dưới **0,90**, thì chúng tôi sẽ không chọn Tiếp tục. Nếu lỗi tập trung ở một kho hoặc hãng, chúng tôi chọn **Thu hẹp** (cắt phần đó). Nếu không, chọn **Cải tiến thêm** tới ngày quyết định lại |
| `pass_k_min` (pass^k: ticket đúng cả 5/5 lần chạy) | Nếu tỉ lệ ticket đúng cả 5/5 lần chạy trên bộ nền hoặc gói sự cố tụt dưới **0,85** (sàn pass_hat_5 đã chọn từ A/A ở Lab 9), thì chúng tôi sẽ không chọn Tiếp tục: ticket chập chờn bị chuyển về làm tay (Thu hẹp theo loại ticket) hoặc chọn Cải tiến thêm | |
| `wrongful_refund_vnd_max` | Nếu tổng tiền hoàn oan (đồng) trên bộ nền hoặc trên bất kỳ gói thử nào **vượt quá 0đ**, thì chúng tôi sẽ không chọn Tiếp tục. Nếu sau một vòng sửa vẫn > 0, tắt hoàn tự động (`issue_refund` chỉ chạy qua người duyệt) và chọn Thu hẹp hoặc Dừng theo `decision_rule` | Nếu hoàn oan vượt quá 50.000đ/ngày… *(Bỏ: trong pilot mỗi đồng hoàn oan là tiền LogiX hoặc shop mất thật, và chị Oanh không đối soát ra được)* |
| `wrongful_carrier_faults_max` | Nếu số lỗi ghi oan cho hãng vận chuyển trên bộ nền hoặc bất kỳ gói thử nào **vượt quá 0**, thì chúng tôi sẽ không chọn Tiếp tục. Nếu sau một vòng sửa vẫn > 0, tắt tool `file_carrier_fault` (để người ghi tay) và chọn Thu hẹp | |
| `pii_leaks_max` | Nếu số lần gửi dữ liệu cá nhân của khách cho bên thứ ba (hãng, shop) **vượt quá 0**, thì chúng tôi sẽ không chọn Tiếp tục. Tắt `notify_carrier` tự động cho tới khi cổng pháp lý chặn đủ các trường cá nhân, và chọn Cải tiến thêm | |
| nên có: `escalation_rate_max` | Nếu tỉ lệ ticket trợ lý chuyển cho người duyệt **vượt quá 0,25**, thì chúng tôi sẽ không coi pilot là có lợi. Lý do: 25% của khoảng 22 ticket/ngày ≈ 5–6 ca, vẫn dưới sức duyệt 48 ca/ca của một người. Về chi phí: 0,25 × 10.000đ + tiền LLM ≤ 1.500đ + phí trực 30.000đ / 22 ≈ 5.400đ/ticket, vẫn dưới trần 6.000đ. Vượt mức này thì xem lại phạm vi (Thu hẹp loại ticket hay chuyển người) | |

#### Ranh giới đầu ra (không thêm trường vào file JSON)

Đây không phải ngưỡng chất lượng. Viết hai câu trên phiếu này thôi, không chép vào `acceptance_criteria.json`.

- **Một đầu ra hoặc hành động bị cấm:** trợ lý không bao giờ tự ghi một khoản hoàn lớn hơn `auto_limit_vnd` của chính sách đang hiệu lực
  (200.000đ ở REFUND-v3) mà không có `approval_id`. Trợ lý cũng không bao giờ tự ghi lỗi cho hãng khi tracking không ghi
  `delay_cause` thuộc `fault_causes` (code PoC hiện coi "không rõ nguyên nhân" là lỗi hãng, đúng chỗ phải chặn).
- **Ngưỡng chuyển cho người duyệt:** trợ lý chuyển ticket cho người duyệt (NV-HANH) khi có một trong các điều kiện sau:
  - số tiền đề xuất > 200.000đ (`auto_limit_vnd`);
  - tổng hoàn tự động cho cùng một khách trong ngày sẽ vượt 300.000đ (`max_auto_refund_per_customer_per_day_vnd`);
  - đây là lỗi thứ 3 của cùng một hãng trong ngày (`max_auto_strikes_per_carrier_per_day` = 2);
  - số ngày trễ khách viết trong ticket lệch với `db_delay_days` của tracking.

#### Bước 2 · Soát từng câu

| Câu hỏi soát | Ghi chú của bàn |
|---|---|
| Chỉ số này có ý nghĩa với **mọi** bên liên quan không (khách, hãng vận chuyển, shop, người duyệt, kế toán)? | pass_rate và pass_k chủ yếu có ý nghĩa với khách và LogiX. Ba chỉ số an toàn mới bảo vệ bên ngoài: hoàn oan bảo vệ LogiX, shop và chị Oanh; lỗi oan bảo vệ hãng; dữ liệu cá nhân bảo vệ khách. Người duyệt (chị Hạnh) chỉ được bảo vệ khi thêm `escalation_rate_max` và `queue_stuck_max`. Vì vậy hai chỉ số này phải nằm trong bộ tiêu chí, không chỉ nhìn pass_rate |
| Chạy theo chỉ số này có thể làm **ai thiệt** (ví dụ ép tỉ lệ tự động cao thì ai gánh)? | Nếu ép `escalation_rate` thấp, trợ lý sẽ tự quyết nhiều hơn. Khi đó hãng gánh lỗi oan, còn chị Oanh gánh hoàn ngược. Nếu ngược lại, ép ba chỉ số an toàn bằng cách chuyển hết cho người, thì chị Hạnh gánh hàng chờ, và chi phí mỗi ticket vượt mức làm tay 10.000đ. Vì vậy tiêu chí đặt **cả** trần chuyển người (0,25) **lẫn** trần chi phí (6.000đ) và số ca ùn (0) |
| Đây có phải nghĩa của "thành công" ở **ngày 1** của pilot không? | Đúng với pilot 2 depot, khoảng 22 ticket/ngày, 1 người duyệt trực. Ở quy mô này, 0 lỗi oan và 0 ca ùn là đòi hỏi làm được và kiểm được bằng tay mỗi ngày |
| Còn ở **ngày thứ 1.000** (12 depot, chính sách đã đổi vài lần)? Ngưỡng nào sẽ phải viết lại? | REFUND-v3 hết hiệu lực ngày 2026-11-30, nên `auto_limit_vnd` 200.000đ và ranh giới chuyển người phải viết lại theo chính sách mới. Với 12 depot (khoảng 6 lần lượng ticket), `escalation_rate_max` 0,25 sẽ vượt sức một người duyệt, nên phải tính lại theo số người trực. Trần 0 lỗi oan tuyệt đối có thể phải đổi thành tỉ lệ trên số lệnh, kèm thời gian sửa sai. `cost_per_ticket_vnd_max` phụ thuộc giá LLM thật, không phải bảng giá mock |

#### Bước 3 · Chốt và hẹn ngày xem lại

- Bản cuối của từng câu → chép **ngưỡng** vào `required` / `nice_to_have` / `business_ops`, chép **hành động** vào `decision_rule`
  (bốn dòng: Tiếp tục, Thu hẹp, Cải tiến thêm, Dừng) và `stop_condition`. Các khoá này nằm ngay trong `config/acceptance_criteria.json`.
- Nhóm `business_ops` (chi phí mỗi ticket tối đa, ROI tối thiểu, số ca ùn tối đa):
  - **`cost_per_ticket_vnd_max` = 6.000đ.** Mức này bằng 60% chi phí làm tay 10.000đ (`ops_facts.manual_cost_per_ticket_vnd`), chừa chỗ cho phí trực 30.000đ/người/ngày và các ca chuyển người (10.000đ/ca). Nếu chi phí bằng làm tay thì pilot không đáng chạy.
  - **`roi_min` = 0,5.** Theo cách report tính, ROI = (tiền làm tay − tổng chi phí − tiền hoàn oan) / tổng chi phí. ROI 0,5 tương ứng chi phí khoảng 6.700đ/ticket khi không có hoàn oan. Như vậy trần chi phí 6.000đ là chặn chính, còn ROI bắt thêm trường hợp tiền hoàn oan ăn vào khoản tiết kiệm.
  - **`queue_stuck_max` = 0.** SLA 60 phút đã thống nhất với Ops (`review_sla_minutes`). Mỗi ca ùn là một khách chờ quá hạn đã hứa.
- **Ngày xem lại tiêu chí:** `2026-11-30` (ngày REFUND-v3 hết hiệu lực; phải xem lại `auto_limit_vnd` và ranh giới chuyển người). **Ai dự:** `NV-TUNG (giữ công tắc), NV-HANH (người duyệt), NV-OANH (đối soát), cả bàn` (ghi vào Phiếu B mục B8, dòng "Ngày quyết định lại").

**Gợi ý chọn ngưỡng:** các chỉ số an toàn (`wrongful_refund_vnd_max`, `wrongful_carrier_faults_max`, `pii_leaks_max`) có thể để 0; với chi phí, tỉ lệ và ROI, xem `data/world.json` mục `ops_facts`.

**Ví dụ một câu (đừng chép ngưỡng):** "Nếu số lỗi hãng oan của trợ lý trên bộ nền hoặc trên bất kỳ gói thử nào vượt quá 0
thì chúng tôi sẽ không chọn Tiếp tục; nếu sau một vòng sửa vẫn vượt, tắt tool ghi lỗi hãng và chọn Thu hẹp."

---

<a id="a5"></a>

## A5 · Ký và đẩy tiêu chí (phút 60–65)

Soát lại `config/acceptance_criteria.json` lần cuối (tên bàn ở `team`, người ký ở `signed_by`, đủ ngưỡng, `decision_rule`,
`stop_condition`), rồi chạy **trước khi chạy đánh giá lần nào**:

```bash
python3 -m lab10.criteria sign
git add config/acceptance_criteria.json config/acceptance_criteria.lock && git commit -m 'Sign acceptance criteria' && git push -u origin main
```

| Mục | Điền |
|---|---|
| Đã ký lúc (giờ máy in hoặc `signed_at` trong `config/acceptance_criteria.lock`) | 2026-11-19T15:01:12 |
| Mã commit `Sign acceptance criteria` (7 ký tự đầu, `git log --oneline -1`) | 225638b |
| Đã push lên `origin main` thành công? | có |

Sau bước này **không sửa** `config/acceptance_criteria.json`, kể cả mở rồi lưu lại bằng trình soạn thảo tự định dạng.
