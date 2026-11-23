import json
import math
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Soi Cầu GĐB 5 Số - Gom Cầu Ăn Thông & Dàn 55/65/75",
    page_icon="🎯",
    layout="wide",
)

st.markdown(
    """
    <style>
    .dan-box {
        background: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.25);
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 10px;
        max-width: 100%;
        overflow-wrap: anywhere;
        word-break: break-word;
    }
    .dan-chips {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-top: 6px;
    }
    .so-chip {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 6px;
        font-family: monospace;
        font-weight: 600;
        font-size: 0.9rem;
        background: rgba(59, 130, 246, 0.14);
        border: 1px solid rgba(59, 130, 246, 0.35);
    }
    .copy-raw-text {
        font-family: monospace;
        font-size: 0.88rem;
        line-height: 1.5;
        white-space: pre-wrap;
        overflow-wrap: anywhere;
        word-break: break-word;
        margin-top: 8px;
        padding: 8px 10px;
        border-radius: 8px;
        background: rgba(0, 0, 0, 0.18);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

BONG_DUONG = {0: 5, 1: 6, 2: 7, 3: 8, 4: 9, 5: 0, 6: 1, 7: 2, 8: 3, 9: 4}
BONG_AM = {1: 4, 4: 1, 2: 9, 9: 2, 3: 6, 6: 3, 5: 8, 8: 5, 0: 7, 7: 0}

DU_LIEU_MAC_DINH = """03917
80129
74446
53046
24502
62477
95014
38926
03372
73683
74129
43454
75451
20893
61225
97403
29865
21915
15178"""


def render_copy_button(text_to_copy: str, label: str = "📋 Copy dàn số", key_suffix: str = "1"):
    payload = json.dumps(text_to_copy)
    components.html(
        f"""
        <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap; margin:4px 0 8px 0;">
            <button id="btn_{key_suffix}" onclick="copyDan_{key_suffix}()" style="
                background: linear-gradient(135deg, #2563eb, #1d4ed8);
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 700;
                cursor: pointer;
                box-shadow: 0 3px 10px rgba(37, 99, 235, 0.35);
            ">{label}</button>
            <span id="status_{key_suffix}" style="font-size:13px; font-weight:600; color:#16a34a;"></span>
        </div>
        <script>
        function copyDan_{key_suffix}() {{
            const txt = {payload};
            const stEl = document.getElementById("status_{key_suffix}");
            if (navigator.clipboard && navigator.clipboard.writeText) {{
                navigator.clipboard.writeText(txt).then(() => {{
                    stEl.innerText = "✓ Đã copy vào bộ nhớ tạm!";
                }}).catch(() => {{
                    fallbackCopy_{key_suffix}(txt, stEl);
                }});
            }} else {{
                fallbackCopy_{key_suffix}(txt, stEl);
            }}
        }}
        function fallbackCopy_{key_suffix}(txt, stEl) {{
            const ta = document.createElement("textarea");
            ta.value = txt;
            ta.style.position = "fixed";
            ta.style.left = "-9999px";
            document.body.appendChild(ta);
            ta.select();
            try {{
                document.execCommand("copy");
                stEl.innerText = "✓ Đã copy vào bộ nhớ tạm!";
            }} catch (e) {{
                stEl.style.color = "#dc2626";
                stEl.innerText = "Hãy bôi đen đoạn số bên dưới và nhấn Ctrl+C.";
            }}
            document.body.removeChild(ta);
        }}
        </script>
        """,
        height=46,
    )


def render_dan_co_dong(dan_so: list[str], delimiter: str = " "):
    chips_html = "".join(f'<span class="so-chip">{s}</span>' for s in dan_so)
    chuoi_thuan = delimiter.join(dan_so)
    st.markdown(
        f"""
        <div class="dan-box">
            <div class="dan-chips">{chips_html}</div>
            <div class="copy-raw-text">{chuoi_thuan}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def chuan_hoa_5so(raw_text: str) -> list[str]:
    ket_qua = []
    for line in raw_text.splitlines():
        digits = "".join(ch for ch in line.strip() if ch.isdigit())
        if digits:
            ket_qua.append(digits.zfill(5)[-5:])
    return ket_qua


def lay_dai_so(so_goc: int, tien: int, lui: int, che_do_bong: str) -> list[int]:
    kq: list[int] = []
    for buoc in range(-lui, tien + 1):
        val = (so_goc + buoc) % 10
        if val not in kq:
            kq.append(val)
        if che_do_bong == "Bóng dương" and BONG_DUONG[val] not in kq:
            kq.append(BONG_DUONG[val])
        elif che_do_bong == "Bóng âm" and BONG_AM[val] not in kq:
            kq.append(BONG_AM[val])
    return kq


def trung_tieu_chi(de_2so: str, tap_so: set[int], che_do: str) -> bool:
    dau = int(de_2so[0])
    duoi = int(de_2so[1])
    tong = (dau + duoi) % 10
    if che_do == "Chạm":
        return (dau in tap_so) or (duoi in tap_so)
    if che_do == "Tổng":
        return tong in tap_so
    if che_do == "Đầu":
        return dau in tap_so
    if che_do == "Đuôi":
        return duoi in tap_so
    return False


def danh_gia_1_vi_tri(
    ds_5so: list[str], vt: int, che_do: str, tien: int, lui: int, che_do_bong: str
) -> dict:
    dung = 0
    sai = 0
    streak_cur = 0
    streak_max = 0
    ket_qua_tung_ky = []

    for i in range(len(ds_5so) - 1):
        so_nguon = int(ds_5so[i][vt - 1])
        dai_so = lay_dai_so(so_nguon, tien, lui, che_do_bong)
        de_sau = ds_5so[i + 1][-2:]
        ok = trung_tieu_chi(de_sau, set(dai_so), che_do)
        ket_qua_tung_ky.append(1 if ok else 0)

        if ok:
            dung += 1
            streak_cur += 1
            if streak_cur > streak_max:
                streak_max = streak_cur
        else:
            sai += 1
            streak_cur = 0

    tong_soi = dung + sai
    ty_le_tong = round((dung / tong_soi) * 100, 2) if tong_soi else 0.0

    # Tỷ lệ 5 kỳ gần nhất để phản ánh rõ khi vừa thua 1 tay gần đây
    gan_5 = ket_qua_tung_ky[-5:] if ket_qua_tung_ky else []
    ty_le_5ky = round((sum(gan_5) / len(gan_5)) * 100, 2) if gan_5 else 0.0

    so_cuoi = int(ds_5so[-1][vt - 1])
    dai_ky_toi = lay_dai_so(so_cuoi, tien, lui, che_do_bong)

    diem_on_dinh = round(
        streak_cur * 12.0 + ty_le_5ky * 0.5 + ty_le_tong * 0.35 + streak_max * 2.0,
        2,
    )

    return {
        "Chế độ": che_do,
        "Vị trí": f"VT{vt}",
        "Ăn thông hiện tại": streak_cur,
        "Ăn thông max": streak_max,
        "Tỷ lệ 5 kỳ (%)": ty_le_5ky,
        "Tỷ lệ tổng (%)": ty_le_tong,
        "Đúng/Tổng": f"{dung}/{tong_soi}",
        "Điểm ổn định": diem_on_dinh,
        "Gốc kỳ cuối": so_cuoi,
        "Dải số kỳ tới": "".join(str(x) for x in dai_ky_toi),
        "_dai_list": dai_ky_toi,
        "_streak_cur": streak_cur,
        "_ty_le_tong": ty_le_tong,
        "_ty_le_5ky": ty_le_5ky,
    }


def quet_cac_cau_tien_lui(
    ds_5so: list[str],
    vi_tri_chon: list[int],
    che_do_bong: str,
    max_tien: int = 8,
    max_lui: int = 8,
    min_streak_cur: int = 1,
    min_ty_le: float = 50.0,
):
    """Quét toàn bộ cặp (Tiến, Lùi) và lọc ra TẤT CẢ cầu đang ăn thông."""
    cac_che_do = ["Chạm", "Tổng", "Đầu", "Đuôi"]
    all_rows = []
    cau_dang_an_thong = []

    for tien in range(0, max_tien + 1):
        for lui in range(0, max_lui + 1):
            so_vt_an_thong_hien_tai = 0
            max_streak_cur_cau = 0
            max_streak_max_cau = 0
            tong_dung = 0
            tong_lan = 0
            tin_hieu_cua_cau = []

            for cd in cac_che_do:
                for vt in vi_tri_chon:
                    res = danh_gia_1_vi_tri(ds_5so, vt, cd, tien, lui, che_do_bong)
                    d, t = map(int, res["Đúng/Tổng"].split("/"))
                    tong_dung += d
                    tong_lan += t
                    max_streak_max_cau = max(max_streak_max_cau, res["Ăn thông max"])

                    if res["_streak_cur"] > 0:
                        so_vt_an_thong_hien_tai += 1
                        max_streak_cur_cau = max(max_streak_cur_cau, res["_streak_cur"])

                    # Điều kiện đưa tín hiệu vào dàn: đang ăn thông >= min_streak_cur và đạt tỷ lệ tối thiểu
                    if res["_streak_cur"] >= min_streak_cur and res["_ty_le_tong"] >= min_ty_le:
                        trong_so = (
                            res["_streak_cur"] * 15.0
                            + res["_ty_le_5ky"] * 0.6
                            + res["_ty_le_tong"] * 0.4
                        )
                        tin_hieu_cua_cau.append({
                            "cau": f"Tiến {tien} - Lùi {lui}",
                            "tien": tien,
                            "lui": lui,
                            "che_do": cd,
                            "vi_tri": res["Vị trí"],
                            "streak_cur": res["_streak_cur"],
                            "ty_le_5ky": res["_ty_le_5ky"],
                            "ty_le_tong": res["_ty_le_tong"],
                            "trong_so": trong_so,
                            "tap": set(res["_dai_list"]),
                        })

            ty_le_tb = round((tong_dung / tong_lan) * 100, 2) if tong_lan else 0.0
            diem_cau = round(
                max_streak_cur_cau * 20.0
                + so_vt_an_thong_hien_tai * 5.0
                + ty_le_tb * 0.5
                + max_streak_max_cau * 2.0,
                2,
            )

            row_dict = {
                "Tiến": tien,
                "Lùi": lui,
                "Cầu": f"Tiến {tien} - Lùi {lui}",
                "Streak hiện tại": max_streak_cur_cau,
                "Số VT đang ăn": so_vt_an_thong_hien_tai,
                "Tỷ lệ ăn TB (%)": ty_le_tb,
                "Ăn thông max": max_streak_max_cau,
                "Điểm cầu": diem_cau,
                "_tin_hieu": tin_hieu_cua_cau,
            }
            all_rows.append(row_dict)

            if max_streak_cur_cau >= min_streak_cur and tin_hieu_cua_cau:
                cau_dang_an_thong.append(row_dict)

    df_all = (
        pd.DataFrame([{k: v for k, v in r.items() if not k.startswith("_")} for r in all_rows])
        .sort_values(
            by=["Streak hiện tại", "Số VT đang ăn", "Tỷ lệ ăn TB (%)", "Điểm cầu"],
            ascending=[False, False, False, False],
        )
        .reset_index(drop=True)
    )

    cau_dang_an_thong.sort(
        key=lambda x: (
            x["Streak hiện tại"],
            x["Số VT đang ăn"],
            x["Tỷ lệ ăn TB (%)"],
            x["Điểm cầu"],
        ),
        reverse=True,
    )

    # Gom TẤT CẢ tín hiệu từ các cầu đang ăn thông
    tat_ca_tin_hieu = []
    for c in cau_dang_an_thong:
        tat_ca_tin_hieu.extend(c["_tin_hieu"])

    # Dự phòng nếu ngưỡng lọc quá gắt khiến danh sách rỗng: lấy tín hiệu có streak_cur cao nhất
    if not tat_ca_tin_hieu and all_rows:
        best_fallback = []
        for cd in cac_che_do:
            for vt in vi_tri_chon:
                r_fb = danh_gia_1_vi_tri(ds_5so, vt, cd, 4, 4, che_do_bong)
                best_fallback.append({
                    "cau": "Dự phòng Tiến 4 - Lùi 4",
                    "tien": 4,
                    "lui": 4,
                    "che_do": cd,
                    "vi_tri": r_fb["Vị trí"],
                    "streak_cur": r_fb["_streak_cur"],
                    "ty_le_5ky": r_fb["_ty_le_5ky"],
                    "ty_le_tong": r_fb["_ty_le_tong"],
                    "trong_so": max(r_fb["Điểm ổn định"], 1.0),
                    "tap": set(r_fb["_dai_list"]),
                })
        best_fallback.sort(key=lambda x: x["trong_so"], reverse=True)
        tat_ca_tin_hieu = best_fallback[:6]

    return df_all, cau_dang_an_thong, tat_ca_tin_hieu


def cham_diem_va_cat_dan(tin_hieu_list: list[dict], so_luong_dan: int):
    bang_diem = []
    for num in range(100):
        s = f"{num:02d}"
        dau, duoi = num // 10, num % 10
        tong = (dau + duoi) % 10
        tong_diem = 0.0
        so_khop = 0

        for sig in tin_hieu_list:
            cd, tap, w = sig["che_do"], sig["tap"], sig["trong_so"]
            khop = (
                (cd == "Chạm" and ((dau in tap) or (duoi in tap)))
                or (cd == "Tổng" and (tong in tap))
                or (cd == "Đầu" and (dau in tap))
                or (cd == "Đuôi" and (duoi in tap))
            )
            if khop:
                tong_diem += w
                so_khop += 1

        bang_diem.append({
            "Số": s,
            "Điểm": round(tong_diem, 2),
            "Số cầu ăn thông khớp": so_khop,
        })

    df_diem = (
        pd.DataFrame(bang_diem)
        .sort_values(
            by=["Điểm", "Số cầu ăn thông khớp", "Số"], ascending=[False, False, True]
        )
        .reset_index(drop=True)
    )
    dan_chon = sorted(df_diem.head(so_luong_dan)["Số"].tolist())
    return df_diem, dan_chon


def tinh_diem_vao_tien(
    so_luong_so: int,
    von_lo_luy_ke: int,
    gia_1_diem: int,
    tien_trung_1_diem: int,
    lai_muc_tieu: int,
    diem_co_ban: int = 1,
) -> dict:
    lai_1_diem = tien_trung_1_diem - (so_luong_so * gia_1_diem)
    can_thu_ve = max(0, von_lo_luy_ke + lai_muc_tieu)

    if lai_1_diem > 0:
        diem_can = max(diem_co_ban, math.ceil(can_thu_ve / lai_1_diem))
    else:
        diem_can = diem_co_ban

    von_tay_nay = so_luong_so * diem_can * gia_1_diem
    tong_von_luy_ke = von_lo_luy_ke + von_tay_nay
    tien_trung_neu_an = diem_can * tien_trung_1_diem
    lai_rong_neu_an = tien_trung_neu_an - tong_von_luy_ke

    return {
        "diem_so": diem_can,
        "von_tay_nay": von_tay_nay,
        "tong_von_luy_ke": tong_von_luy_ke,
        "tien_trung_neu_an": tien_trung_neu_an,
        "lai_rong_neu_an": lai_rong_neu_an,
        "lai_1_diem": lai_1_diem,
    }


def backtest_gom_cau_an_thong(
    ds_5so: list[str],
    vi_tri_chon: list[int],
    che_do_bong: str,
    so_luong_dan: int,
    min_streak_cur: int,
    min_ty_le: float,
    gia_1_diem: int,
    tien_trung_1_diem: int,
    lai_muc_tieu: int,
    von_ban_dau: int,
    moc_chot_lai: int,
):
    rows = []
    bang_von_rows = []
    bang_chot_lai_rows = []

    streak_cur = 0
    streak_max = 0
    an_cnt = 0
    truot_cnt = 0

    von_lo_luy_ke = 0
    loi_nhuan_thuc_te = 0
    tong_von_da_vao = 0

    for idx in range(2, len(ds_5so) - 1):
        lich_su_toi_ky = ds_5so[: idx + 1]
        _, _, tin_hieu_ky = quet_cac_cau_tien_lui(
            lich_su_toi_ky,
            vi_tri_chon=vi_tri_chon,
            che_do_bong=che_do_bong,
            max_tien=6,
            max_lui=6,
            min_streak_cur=min_streak_cur,
            min_ty_le=min_ty_le,
        )
        _, dan_ky = cham_diem_va_cat_dan(tin_hieu_ky, so_luong_dan)

        plan = tinh_diem_vao_tien(
            so_luong_so=len(dan_ky),
            von_lo_luy_ke=von_lo_luy_ke,
            gia_1_diem=gia_1_diem,
            tien_trung_1_diem=tien_trung_1_diem,
            lai_muc_tieu=lai_muc_tieu,
        )

        tong_von_da_vao += plan["von_tay_nay"]
        von_kha_dung_truoc_tay = von_ban_dau + loi_nhuan_thuc_te
        du_von_tay_nay = von_kha_dung_truoc_tay >= plan["von_tay_nay"]

        de_ky_sau = ds_5so[idx + 1][-2:]
        is_an = de_ky_sau in set(dan_ky)

        if is_an:
            an_cnt += 1
            streak_cur += 1
            if streak_cur > streak_max:
                streak_max = streak_cur
            loi_tay = plan["tien_trung_neu_an"] - plan["tong_von_luy_ke"]
            loi_nhuan_thuc_te += loi_tay
            von_lo_luy_ke = 0
        else:
            truot_cnt += 1
            streak_cur = 0
            loi_tay = -plan["von_tay_nay"]
            loi_nhuan_thuc_te += loi_tay
            von_lo_luy_ke = plan["tong_von_luy_ke"]

        von_hien_tai = von_ban_dau + loi_nhuan_thuc_te
        dat_moc_chot = loi_nhuan_thuc_te >= moc_chot_lai
        ky_label = f"#{idx + 2} ({ds_5so[idx + 1]})"

        rows.append({
            "Kỳ KQ": ky_label,
            "Đề": de_ky_sau,
            "Điểm/số": plan["diem_so"],
            "Vốn tay": f"{plan['von_tay_nay']:,}đ",
            "Tiền trúng": f"{plan['tien_trung_neu_an']:,}đ" if is_an else "0đ",
            "Lãi/Lỗ tay": f"{loi_tay:+,}đ",
            "Lãi/Lỗ lũy kế": f"{loi_nhuan_thuc_te:+,}đ",
            "Trạng thái": "ĂN" if is_an else "TRƯỢT",
        })

        bang_von_rows.append({
            "Kỳ KQ": ky_label,
            "Vốn đầu kỳ": f"{von_kha_dung_truoc_tay:,}đ",
            "Vốn vào tay": f"{plan['von_tay_nay']:,}đ",
            "Lỗ dồn lũy kế": f"{von_lo_luy_ke:,}đ",
            "Tổng vốn đã đánh": f"{tong_von_da_vao:,}đ",
            "Vốn còn lại": f"{von_hien_tai:,}đ",
            "Mức vốn": "Đủ vốn" if du_von_tay_nay else "Thiếu vốn",
        })

        bang_chot_lai_rows.append({
            "Kỳ KQ": ky_label,
            "Kết quả": "ĂN" if is_an else "TRƯỢT",
            "Lãi/Lỗ tay": f"{loi_tay:+,}đ",
            "Lãi ròng lũy kế": f"{loi_nhuan_thuc_te:+,}đ",
            "Mốc chốt lãi": f"{moc_chot_lai:,}đ",
            "Chốt lãi": "ĐẠT MỐC CHỐT" if dat_moc_chot else "Chưa đạt",
        })

    ke_hoach_next = tinh_diem_vao_tien(
        so_luong_so=so_luong_dan,
        von_lo_luy_ke=von_lo_luy_ke,
        gia_1_diem=gia_1_diem,
        tien_trung_1_diem=tien_trung_1_diem,
        lai_muc_tieu=lai_muc_tieu,
    )

    tong = an_cnt + truot_cnt
    ty_le_an = round((an_cnt / tong) * 100, 2) if tong else 0.0
    von_hien_tai = von_ban_dau + loi_nhuan_thuc_te

    tom_tat = {
        "Số lần ĂN": an_cnt,
        "Số lần TRƯỢT": truot_cnt,
        "Tỷ lệ ĂN (%)": ty_le_an,
        "Ăn thông max": streak_max,
        "Lãi/Lỗ tích lũy": loi_nhuan_thuc_te,
        "Vốn hiện tại": von_hien_tai,
        "Tổng vốn đã đánh": tong_von_da_vao,
        "Lỗ đang treo": von_lo_luy_ke,
        "Đạt mốc chốt lãi": loi_nhuan_thuc_te >= moc_chot_lai,
    }
    return (
        pd.DataFrame(rows),
        pd.DataFrame(bang_von_rows),
        pd.DataFrame(bang_chot_lai_rows),
        tom_tat,
        ke_hoach_next,
    )


# ---------------- SESSION STATE ----------------
if "raw_gdb_text" not in st.session_state:
    st.session_state.raw_gdb_text = DU_LIEU_MAC_DINH
if "quick_add_input" not in st.session_state:
    st.session_state.quick_add_input = ""


def them_so_nhanh_enter():
    val = st.session_state.quick_add_input.strip()
    digits = "".join(ch for ch in val if ch.isdigit())
    if digits:
        so_5 = digits.zfill(5)[-5:]
        current = st.session_state.raw_gdb_text.rstrip()
        st.session_state.raw_gdb_text = f"{current}\n{so_5}" if current else so_5
    st.session_state.quick_add_input = ""


# ---------------- GIAO DIỆN ----------------
st.title("🎯 Soi Cầu GĐB 5 Số - Gom Tất Cả Cầu Đang Ăn Thông")

with st.expander("📥 Nhập liệu GĐB 5 số (nhấn Enter tự nhận & cập nhật ngay)", expanded=True):
    st.text_input(
        "⚡ Nhập nhanh 1 kỳ mới (5 số) rồi nhấn ENTER:",
        key="quick_add_input",
        on_change=them_so_nhanh_enter,
        placeholder="Ví dụ: 48291 rồi nhấn Enter...",
    )
    col_in, col_up = st.columns([3, 1])
    with col_in:
        st.text_area(
            "Danh sách dữ liệu GĐB (mỗi dòng 1 kỳ, từ cũ -> mới):",
            key="raw_gdb_text",
            height=115,
        )
    with col_up:
        up_file = st.file_uploader("Hoặc tải file .txt / .csv", type=["txt", "csv"])
        if up_file is not None:
            st.session_state.raw_gdb_text = up_file.getvalue().decode(
                "utf-8", errors="ignore"
            )
            st.rerun()

ds_5so = chuan_hoa_5so(st.session_state.raw_gdb_text)
st.info(
    f"Đã nhận **{len(ds_5so)}** kỳ | Kỳ mới nhất: **`{ds_5so[-1] if ds_5so else '---'}`** | "
    f"Đề kỳ mới nhất: **`{ds_5so[-1][-2:] if ds_5so else '--'}`**"
)

if len(ds_5so) < 4:
    st.warning("Cần ít nhất 4 kỳ GĐB để đánh giá cầu ăn thông và kiểm tra lịch sử.")
    st.stop()

c1, c2, c3, c4, c5 = st.columns([2, 1.3, 1.3, 1.4, 1.3])
with c1:
    vi_tri_chon = st.multiselect(
        "Phạm vi vị trí xét (VT1..VT5)",
        options=[1, 2, 3, 4, 5],
        default=[1, 2, 3, 4, 5],
        format_func=lambda x: f"VT{x}",
    )
with c2:
    min_streak_cur = int(
        st.number_input("Ăn thông hiện tại ≥", min_value=1, max_value=10, value=1, step=1)
    )
with c3:
    min_ty_le = float(
        st.slider("Tỷ lệ ăn tối thiểu (%)", min_value=0.0, max_value=100.0, value=50.0, step=5.0)
    )
with c4:
    che_do_bong = st.selectbox("Bóng", ["Không", "Bóng dương", "Bóng âm"])
with c5:
    so_luong_dan = int(st.selectbox("Dàn số", [55, 65, 75], index=1))

st.markdown("### 💰 Cấu Hình Vốn, Vào Tiền & Chốt Lãi")
v1, v2, v3, v4, v5 = st.columns(5)
with v1:
    von_ban_dau = int(
        st.number_input("Vốn ban đầu (đ)", min_value=1000, max_value=10_000_000_000, value=1_000_000, step=50_000)
    )
with v2:
    gia_1_diem = int(
        st.number_input("Giá 1 điểm (đ)", min_value=100, max_value=10_000_000, value=1000, step=100)
    )
with v3:
    tien_trung_1_diem = int(
        st.number_input("Tiền trúng 1 điểm (đ)", min_value=1000, max_value=500_000_000, value=99900, step=100)
    )
with v4:
    lai_muc_tieu = int(
        st.number_input("Lãi mục tiêu mỗi tay (đ)", min_value=0, max_value=100_000_000, value=10000, step=1000)
    )
with v5:
    moc_chot_lai = int(
        st.number_input("Mốc chốt lãi tổng (đ)", min_value=0, max_value=10_000_000_000, value=100000, step=10000)
    )

if not vi_tri_chon:
    st.warning("Vui lòng chọn ít nhất 1 vị trí.")
    st.stop()

df_all_cau, ds_cau_an_thong, tin_hieu_gom = quet_cac_cau_tien_lui(
    ds_5so=ds_5so,
    vi_tri_chon=sorted(vi_tri_chon),
    che_do_bong=che_do_bong,
    max_tien=8,
    max_lui=8,
    min_streak_cur=min_streak_cur,
    min_ty_le=min_ty_le,
)
df_diem, dan_chon = cham_diem_va_cat_dan(tin_hieu_gom, so_luong_dan)

df_bt, df_von, df_chot_lai, tom_tat_bt, ke_hoach_next = backtest_gom_cau_an_thong(
    ds_5so=ds_5so,
    vi_tri_chon=sorted(vi_tri_chon),
    che_do_bong=che_do_bong,
    so_luong_dan=so_luong_dan,
    min_streak_cur=min_streak_cur,
    min_ty_le=min_ty_le,
    gia_1_diem=gia_1_diem,
    tien_trung_1_diem=tien_trung_1_diem,
    lai_muc_tieu=lai_muc_tieu,
    von_ban_dau=von_ban_dau,
    moc_chot_lai=moc_chot_lai,
)

st.success(
    f"🔥 Đã tự động gom **{len(ds_cau_an_thong)}** cầu Tiến/Lùi đang ăn thông "
    f"với tổng cộng **{len(tin_hieu_gom)}** tín hiệu (Chạm/Tổng/Đầu/Đuôi) đạt chuẩn để tạo dàn **{len(dan_chon)} số**."
)

tab1, tab2, tab3, tab4 = st.tabs([
    f"🎲 Dàn {len(dan_chon)} Số & Copy Nổi",
    "🔥 Các Cầu Đang Ăn Thông Được Gom",
    "💼 Bảng Vốn & Bảng Chốt Lãi",
    "📜 Lịch Sử ĂN / TRƯỢT",
])

with tab1:
    dinh_dang_copy = st.radio(
        "Định dạng dàn số",
        ["Cách nhau dấu cách (01 02 03...)", "Cách nhau dấu phẩy (01, 02, 03...)"],
        horizontal=True,
    )
    chuoi_copy = (
        " ".join(dan_chon)
        if dinh_dang_copy.startswith("Cách nhau dấu cách")
        else ", ".join(dan_chon)
    )
    delim = " " if dinh_dang_copy.startswith("Cách nhau dấu cách") else ", "

    render_copy_button(chuoi_copy, label=f"📋 COPY DÀN {len(dan_chon)} SỐ", key_suffix="gom")
    render_dan_co_dong(dan_chon, delimiter=delim)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Vào đề xuất kỳ tới", f"{ke_hoach_next['diem_so']} điểm/số")
    k2.metric("Vốn cần tay tới", f"{ke_hoach_next['von_tay_nay']:,}đ")
    k3.metric("Tiền trúng (nếu ăn)", f"{ke_hoach_next['tien_trung_neu_an']:,}đ")
    k4.metric("Lãi ròng dự kiến", f"{ke_hoach_next['lai_rong_neu_an']:+,}đ")

    st.markdown("#### Chi tiết các tín hiệu ăn thông đang góp mặt tạo dàn")
    st.dataframe(
        pd.DataFrame([
            {
                "Cầu": s["cau"],
                "Chế độ": s["che_do"],
                "Vị trí": s["vi_tri"],
                "Streak hiện tại": s["streak_cur"],
                "Tỷ lệ 5 kỳ (%)": s["ty_le_5ky"],
                "Tỷ lệ tổng (%)": s["ty_le_tong"],
                "Dải số": "".join(str(x) for x in sorted(s["tap"])),
            }
            for s in tin_hieu_gom
        ]),
        use_container_width=True,
        hide_index=True,
    )

with tab2:
    st.subheader("Danh sách tất cả cầu Tiến / Lùi đang ăn thông (được tự động chọn)")
    if ds_cau_an_thong:
        st.dataframe(
            pd.DataFrame([
                {k: v for k, v in c.items() if not k.startswith("_")}
                for c in ds_cau_an_thong
            ]),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.warning("Chưa có cầu nào đạt mức ăn thông/tỷ lệ tối thiểu hiện tại.")

    st.subheader("Toàn bộ bảng quét Tiến / Lùi (0..8)")
    st.dataframe(df_all_cau, use_container_width=True, hide_index=True)

with tab3:
    t1, t2, t3, t4 = st.columns(4)
    t1.metric("Vốn ban đầu", f"{von_ban_dau:,}đ")
    t2.metric("Vốn hiện tại", f"{tom_tat_bt['Vốn hiện tại']:,}đ")
    t3.metric("Lãi/Lỗ tích lũy", f"{tom_tat_bt['Lãi/Lỗ tích lũy']:+,}đ")
    t4.metric(
        "Trạng thái chốt lãi",
        "ĐẠT MỐC CHỐT" if tom_tat_bt["Đạt mốc chốt lãi"] else "CHƯA ĐẠT",
    )

    st.subheader("💼 Bảng Vốn")
    st.dataframe(df_von, use_container_width=True, hide_index=True)

    st.subheader("💵 Bảng Chốt Lãi")
    st.dataframe(df_chot_lai, use_container_width=True, hide_index=True)

with tab4:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Số lần ĂN", tom_tat_bt["Số lần ĂN"])
    m2.metric("Số lần TRƯỢT", tom_tat_bt["Số lần TRƯỢT"])
    m3.metric("Tỷ lệ ĂN", f"{tom_tat_bt['Tỷ lệ ĂN (%)']}%")
    m4.metric("Ăn thông max", tom_tat_bt["Ăn thông max"])

    st.dataframe(df_bt, use_container_width=True, hide_index=True)