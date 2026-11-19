# Team

## Thông tin nhóm

- Tên nhóm (`TenNhom`, không dấu, không khoảng trắng): TenNhom321
- Lớp: `L3B`
- Repo của bàn: `K5-L3B-DAY10-TenNhom321-PoCtoPilotGate1`
- Thẻ sự cố đã bốc (S1–S8): S1

## Thành viên

Họ tên đầy đủ và MSSV của **mọi** thành viên; bàn 3 người thì để trống dòng 4. Vai: Kỹ sư cổng · Sản phẩm và kinh doanh · Vận hành và pháp lý (README mục 3, phút 0–15).

| STT | Họ và tên | MSSV | Vai | Trưởng nhóm |
| --: | --------- | ---- | --- | :---------: |
|   1 | Trịnh Ngọc Ninh | 2A202603996 | Sản phẩm và kinh doanh |             |
|   2 | Nguyễn Thanh Tùng | 2A202603957 | Kỹ sư cổng | ✔ |
|   3 | Giang Thái Sơn | 2A202603964 | Vận hành và pháp lý |             |
|   4 |           |      |     |             |

Ghi `members` trong `submission/submission.json` theo dạng `"HoVaTen-MSSV"`, khớp bảng trên.

Ghi chú về commit: các commit của bàn (`225638b`, `f0c2abb`, `5d327a8` và commit vòng 2) đều mang danh tính git của trưởng nhóm `2A202603957` vì cả bàn làm trên một máy. Phần việc của từng người được ghi ở các mục cá nhân dưới đây, kèm mã lần chạy và mục phiếu làm bằng chứng.

## Cá nhân

Mỗi thành viên tự viết một mục bên dưới (chép mẫu, đổi tiêu đề thành họ tên không dấu và MSSV, ví dụ `## NguyenVanAn-20241234`).

## TrinhNgocNinh-2A202603996

### Phần việc phụ trách

Vai **Sản phẩm và kinh doanh**. Phiếu A (tiêu chí chấp nhận, ký trước khi đo); Phiếu B mục B3 (bản đồ dữ liệu), B8 (quyết định Gate 1 v1); Phiếu C mục C12 (quyết định v2) và dòng rủi ro chi phí ở C10. File: `config/acceptance_criteria.json` (phần `business_ops`, `decision_rule`), `config/operating_gates.json` mục `business` (trần tiền, ngân sách mỗi ticket, phạm vi pilot, ROI tối thiểu).

### Đóng góp cụ thể

- Đặt các ngưỡng đã ký trước khi đo: `pass_rate` ≥ 0,9, `pass_k` ≥ 0,85, ba chỉ số an toàn = 0, `cost_per_ticket_vnd` ≤ 6.000, `roi` ≥ 0,5, `queue_stuck` = 0, và bốn dòng `decision_rule`; ký và đẩy lên trước lần chạy đầu tiên (commit `225638b`, hash tiêu chí `9ce943f7`).
- Chọn cấu hình kinh doanh vòng 1 từ các lần thử: trần hoàn tự động 1.000.000đ/ngày, ngân sách LLM 1.200đ/ticket, phạm vi HN + HCM (độ phủ 0,5909). Thử thêm người trực thứ hai cả ca thì chi phí 7.857đ và ROI 0,27, nên bác.
- Quyết định v1 = **Thu hẹp** (cắt DN, CT, HCM-B2B và ticket không tra được đơn) vì bộ nền đạt cả 9 ngưỡng ở phạm vi còn lại.
- Quyết định v2 = **Cải tiến thêm**: gói S1 an toàn về 0 nhưng chi phí 6.215đ vượt 6.000đ; thử thu hẹp thêm về chỉ HN thì 6.744đ và ROI 0,48, nên không cắt thêm. Ghi rõ rằng không dòng `decision_rule` nào khớp trọn vẹn.
- Đối chiếu pre-mortem vòng 1 với thẻ S1 (C1): chỉ ra ba đường lỗi bàn chưa nghĩ tới (ngày giao trống, khách khai thấp hơn tracking, cửa sổ 7 ngày của hãng).

### Bằng chứng

- Commit: `225638b` (ký tiêu chí), `f0c2abb` (chốt cổng vòng 1, quyết định v1), `5d327a8` (nhận thẻ S1).
- Mã lần chạy: base `R-base-before-20261119-151616-68feb1`; prepared `R-base-prepared-20261119-152526-d3e48b`; thẻ S1 `R-S1-before-20261119-170729-341a08` · `R-S1-prepared-20261119-170729-341a08` · `R-S1-after-20261119-170729-341a08`; thử thu hẹp HN `R-S1-after-20261119-170622-d07c13`.
- Phiếu: A (A1–A5), B3, B8, C10 dòng 3, C12.

**Dùng AI (Claude Code):** để đọc code và report, đề xuất con số thử, soát câu chữ và ghi vào phiếu; các con số đều lấy từ report và đã chạy lại bằng `lab10.eval`. Quyết định ký tiêu chí và chọn v1, v2 là của bàn.

### Exit ticket

- Học được: một ngưỡng chi phí tính trên số ticket mỗi ngày rất nhạy với khối lượng; cắt phạm vi nhỏ hơn có thể làm chi phí mỗi ticket tăng thay vì giảm, vì phí trực cố định chia cho ít ticket.
- Còn chưa chắc: ở khối lượng thật, bao nhiêu ticket mỗi ngày thì chi phí xuống dưới 6.000đ. Con số "khoảng 10 ticket" mới là ước tính, chưa đo.

## NguyenThanhTung-2A202603957

### Phần việc phụ trách

Vai **Kỹ sư cổng**, trưởng nhóm. Code: `lab10/guards.py` (G1 đến G5), `lab10/monitors.py`. Phiếu B mục B4 (HAZOP vòng 1), B7.1 đến B7.3 (cổng và hai ticket thử); Phiếu C mục C4 (HAZOP của thẻ), C5 (specification, giả định môi trường), C6 và C9 (fault tree trước và sau sửa), C7 (bảng sửa), C8 (chỉ số theo dõi mới).

### Đóng góp cụ thể

- **Vòng 1:** viết ba cổng và chốt bằng `lab10.checkpoint` (hash `168ba489`): G1 ghim chính sách theo ngày hiệu lực thay vì cờ `index_active`; G2 chặn hoàn vượt mức hưởng theo tracking, hoàn trùng, phê duyệt không hợp lệ; G3 chỉ ghi lỗi hãng khi `carrier_at_fault`, có trần 2 lỗi/hãng/ngày và chỉ gửi hãng các trường chính sách cho phép.
- **Vòng 2 (thẻ S1):** dò trace S1-07, S1-01, S1-20, S1-21, S1-42, S1-43; thêm **G4** `_delivery_conflict` (kiện đã giao mà thiếu ngày giao, hoặc trễ mà thiếu nguyên nhân thì chuyển người) và **G5** `_gate_reply` (chặn lời từ chối oan khi tracking đủ điều kiện hoàn). Không đọc mã ticket hay câu chữ, chỉ đọc `orders`, `policies`, sổ cái.
- Thêm ba monitor: `max_faults_per_carrier_day`, `claim_vs_db_mismatch_rate`, `delivery_data_conflict_rate`; tự phát hiện và sửa lỗi gộp theo ngày của monitor đầu (báo 1.0 thay vì 4.0 ở mốc base).
- Kiểm không regression: bộ nền 22 ticket × 5 seed vẫn 1.0; kiểm G4 và trần G3 trên S1-20/21/42/43 bằng một lần chạy tạm phạm vi `all`, rồi khôi phục config.
- Ghi nhận phần còn hở: trần theo ngày không bảo vệ cửa sổ 7 ngày của hãng, nên nhánh đó chỉ là "giảm".

### Bằng chứng

- Mã nguồn: `lab10/guards.py`, `lab10/guards_round1.py` (bản chốt), `lab10/monitors.py`.
- Mã lần chạy: `R-base-prepared-20261119-152526-d3e48b`; `R-S1-after-20261119-170728-341a08` (pass 1.0, hoàn sai 0, lỗi oan 0); `R-S1-after-20261119-170012-43ce99` (thử phạm vi `all`, 13/13 ticket đạt); `R-base-after-20261119-170728-341a08` (không regression); `R-S1-grade-20261119-170729-341a08` (5/6 kiểm ✅, kiểm 4 test ẩn không có trên máy này).
- Phiếu: B4, B7.1 đến B7.3, C4 đến C9.

**Dùng AI (Claude Code):** để đọc `agent.py`, `helpers.py`, `tools.py`, dò trace, và soạn đoạn code của G4, G5 và monitor; mọi thay đổi được chạy lại bằng `lab10.eval` và `lab10.grade`. Code không chứa mã ticket hay câu chữ cụ thể (luật 4).

### Exit ticket

- Học được: một cổng chỉ chặn một chiều (hoàn quá nhiều) sẽ bỏ sót chiều ngược lại (từ chối oan); phải hỏi cả "nếu giá trị quá thấp, quá cao, hoặc thiếu thì sao" cho từng tham số.
- Còn chưa chắc: khi LLM lỗi 429 ở tải cao, `fail_open` và `write_retry` có đi qua G4, G5 đúng như mô phỏng hay không; bộ nền không có giờ cao điểm nên chưa đo.

## GiangThaiSon-2A202603964

### Phần việc phụ trách

Vai **Vận hành và pháp lý**. File: `config/operating_gates.json` mục `operations` và `legal`; `submission/submission.json`. Phiếu B mục B5 (checklist 9 nhóm việc), B6 (pre-mortem bốn lăng kính), B7.5 và B7.6 (Runbook 1 đến 3, giờ cao điểm); Phiếu C mục C10 (rủi ro cửa sổ 7 ngày và dữ liệu giao hàng), C11 (cập nhật checklist, Runbook 4 và 5).

### Đóng góp cụ thể

- Cấu hình vận hành vòng 1: PIC `NV-TUNG`, người duyệt `NV-HANH`, 1 người trực, 6 ca/giờ, chờ tối đa 45 phút, kiểm mẫu 10%, `decision_note` bật, kênh báo tin và 5 điều kiện dừng khớp `stop_condition` đã ký (tắt tool trong 30 phút, tắt `notify_carrier` trong 15 phút khi lộ dữ liệu).
- Cấu hình pháp lý: chặn 5 trường cá nhân gửi hãng (`recipient_contact`, `customer_note`, `name`, `phone`, `street`) và `carrier_fault_requires_recorded_cause = true`.
- Viết Runbook 1 đến 3 và giờ cao điểm: tín hiệu, ngưỡng vàng, đỏ và người quyết, mọi con số khớp config và report.
- **Vòng 2:** viết Runbook 4 và 5; thêm `NV-OANH` vào `alert_channel` để người nhận khiếu nại của hãng cũng được báo; đặt ngưỡng runbook cho ba monitor mới (vàng 2, đỏ ≥ 3 lỗi/hãng/ngày) và nêu rõ chúng không được code ép.
- Rà phía pháp lý với bên thứ ba: soạn nội dung trả lời hãng GHSH (rà lỗi trước 17h cùng ngày, nói rõ lỗi nào huỷ vì sao), và ghi nhận ở mốc base `notify_carrier` gửi hãng `customer_note` và quận (G3 cắt ở bản chốt).
- Điền `submission/submission.json` (`incident`, `decision_v1`, `decision_v2`, ba dòng bắt buộc) và chạy `check_submission --collect`.

### Bằng chứng

- Config: `config/operating_gates.json` (mục `operations`, `legal`), bản chốt `config/operating_gates.round1.json`.
- Mã lần chạy: `R-S1-grade-20261119-170729-341a08`; `R-S1-after-20261119-170728-341a08` (0 ca ùn, chờ lâu nhất 0 phút).
- Phiếu: B5, B6, B7.5, B7.6, C10 dòng 1 và 2, C11.

**Dùng AI (Claude Code):** để soạn khung runbook, đối chiếu con số với `config/operating_gates.json` và report, và soát câu chữ; các ngưỡng và tên người lấy từ `data/world.json` (`staff`) và config.

### Exit ticket

- Học được: runbook chỉ có ích khi mọi con số trong đó khớp config và report; và có những ngưỡng (như 3 lỗi trong 7 ngày của hãng) mà code không ép được nên phải dựa vào quy trình người rà.
- Còn chưa chắc: ngưỡng vàng, đỏ của ba monitor mới (2, 3 lỗi/hãng/ngày; 0,10; 0,02) lấy từ mô phỏng một ngày, chưa biết có hợp với dữ liệu thật hay không.
