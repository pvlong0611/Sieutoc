import json
import math
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Soi Cầu GĐB 5 Số - Vào Tiền Gỡ Thắng Reset Về Gốc",
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
    gan_5 = ket_qua_tung_ky[-5:] if ket_qua_tung_ky else []
    ty_le_5ky = round((sum(gan_5) / len(gan_5)) * 100, 2) if gan_5 else 0.0

    so_cuoi = int(ds_5so[-1][vt - 1])
    dai_ky_toi = lay_dai_so(so_cuoi, tien, lui, che_do_bong)

    return {
        "Chế độ": che_do,
        "Vị trí": f"VT{vt}",
        "Tỷ lệ ăn (%)": ty_le_tong,
        "Tỷ lệ 5 kỳ (%)": ty_le_5ky,
        "Ăn thông hiện tại": streak_cur,
        "Ăn thông max": streak_max,
        "Đúng/Tổng": f"{dung}/{tong_soi}",
        "Gốc kỳ cuối": so_cuoi,
        "Dải số kỳ tới": "".join(str(x) for x in dai_ky_toi),
        "_dai_list": dai_ky_toi,
        "_streak_cur": streak_cur,
        "_ty_le_tong": ty_le_tong,
        "_ty_le_5ky": ty_le_5ky,
    }


def loc_cau_dat_chuan_95(
    ds_5so: list[str],
    vi_tri_chon: list[int],
    che_do_bong: str,
    max_tien: int = 8,
    max_lui: int = 8,
    nguong_ty_le: float = 95.0,
    yeu_cau_an_thong: bool = True,
    cho_phep_du_phong: bool = False,
):
    cac_che_do = ["Chạm", "Tổng", "Đầu", "Đuôi"]
    bang_cau_dat_chuan = []
    tin_hieu_dat_chuan = []
    tat_ca_ung_vien = []

    for tien in range(0, max_tien + 1):
        for lui in range(0, max_lui + 1):
            for cd in cac_che_do:
                for vt in vi_tri_chon:
                    res = danh_gia_1_vi_tri(ds_5so, vt, cd, tien, lui, che_do_bong)
                    dat_ty_le = res["_ty_le_tong"] >= nguong_ty_le
                    dat_streak = (res["_streak_cur"] >= 1) if yeu_cau_an_thong else True

                    trong_so = (
                        res["_ty_le_tong"] * 2.0
                        + res["_streak_cur"] * 15.0
                        + res["_ty_le_5ky"] * 0.5
                    )

                    candidate = {
                        "Cầu": f"Tiến {tien} - Lùi {lui}",
                        "Tiến": tien,
                        "Lùi": lui,
                        "Chế độ": cd,
                        "Vị trí": res["Vị trí"],
                        "Tỷ lệ ăn (%)": res["_ty_le_tong"],
                        "Tỷ lệ 5 kỳ (%)": res["_ty_le_5ky"],
                        "Ăn thông hiện tại": res["_streak_cur"],
                        "Ăn thông max": res["Ăn thông max"],
                        "Đúng/Tổng": res["Đúng/Tổng"],
                        "Dải số kỳ tới": res["Dải số kỳ tới"],
                        "_trong_so": trong_so,
                        "_tap": set(res["_dai_list"]),
                    }
                    tat_ca_ung_vien.append(candidate)

                    if dat_ty_le and dat_streak:
                        bang_cau_dat_chuan.append(candidate)
                        tin_hieu_dat_chuan.append(candidate)

    bang_cau_dat_chuan.sort(
        key=lambda x: (
            x["Tỷ lệ ăn (%)"],
            x["Ăn thông hiện tại"],
            x["Ăn thông max"],
            x["Tỷ lệ 5 kỳ (%)"],
        ),
        reverse=True,
    )

    du_phong_da_dung = False
    if not tin_hieu_dat_chuan and cho_phep_du_phong and tat_ca_ung_vien:
        tat_ca_ung_vien.sort(
            key=lambda x: (
                x["Tỷ lệ ăn (%)"],
                x["Ăn thông hiện tại"],
                x["Ăn thông max"],
            ),
            reverse=True,
        )
        tin_hieu_dat_chuan = tat_ca_ung_vien[:5]
        bang_cau_dat_chuan = tin_hieu_dat_chuan
        du_phong_da_dung = True

    df_dat_chuan = pd.DataFrame([
        {k: v for k, v in item.items() if not k.startswith("_")}
        for item in bang_cau_dat_chuan
    ])
    return df_dat_chuan, tin_hieu_dat_chuan, du_phong_da_dung


def cham_diem_siet_dan(tin_hieu_list: list[dict], so_luong_dan: int):
    if not tin_hieu_list:
        df_empty = pd.DataFrame([
            {"Số": f"{i:02d}", "Điểm": 0.0, "Số cầu ≥95% khớp": 0}
            for i in range(100)
        ])
        return df_empty, []

    bang_diem = []
    for num in range(100):
        s = f"{num:02d}"
        dau, duoi = num // 10, num % 10
        tong = (dau + duoi) % 10
        tong_diem = 0.0
        so_khop = 0

        for sig in tin_hieu_list:
            cd, tap, w = sig["Chế độ"], sig["_tap"], sig["_trong_so"]
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
            "Số cầu ≥95% khớp": so_khop,
        })

    df_diem = (
        pd.DataFrame(bang_diem)
        .sort_values(
            by=["Số cầu ≥95% khớp", "Điểm", "Số"],
            ascending=[False, False, True],
        )
        .reset_index(drop=True)
    )

    df_co_tin_hieu = df_diem[df_diem["Điểm"] > 0]
    dan_chon = sorted(df_co_tin_hieu.head(so_luong_dan)["Số"].tolist())
    return df_diem, dan_chon


def tinh_diem_go_reset(
    so_luong_so: int,
    lo_don_hien_tai: int,
    so_tay_thua_lien_tiep: int,
    von_hien_tai: int,
    gia_1_diem: int,
    tien_trung_1_diem: int,
    diem_khoi_dau: int,
    he_so_gap: float,
    lai_bu_toi_thieu: int,
    ty_le_von_toi_da_tay: float,
) -> dict:
    """Thắng tay nào thì tay sau reset về `diem_khoi_dau` (vd: 5đ).
    Nếu thua thì nâng điểm để ăn là đủ bù lỗ dồn + có lãi nhẹ (hoặc nhân theo hệ số).
    """
    if so_luong_so <= 0:
        return {
            "diem_so": 0,
            "goc_danh": 0,
            "tien_trung": 0,
            "lai_neu_an": 0,
            "che_do_tay": "Nghỉ",
        }

    chi_phi_1_diem_dan = so_luong_so * gia_1_diem
    lai_rong_1_diem = tien_trung_1_diem - chi_phi_1_diem_dan

    # Tay đầu chuỗi hoặc sau khi vừa ăn -> luôn về đúng mức khởi đầu (ví dụ 5đ)
    if lo_don_hien_tai <= 0 or so_tay_thua_lien_tiep <= 0:
        diem_de_xuat = diem_khoi_dau
        che_do_tay = "Mức gốc (vừa ăn / khởi đầu)"
    else:
        # Tính số điểm cần để nếu trúng 1 số thì thu đủ lỗ dồn + lãi bù tối thiểu
        if lai_rong_1_diem > 0:
            diem_can_go = math.ceil((lo_don_hien_tai + lai_bu_toi_thieu) / lai_rong_1_diem)
        else:
            diem_can_go = diem_khoi_dau

        # Đồng thời tính bậc nhân theo hệ số (vd 5đ -> 10đ -> 20đ nếu hệ số = 2)
        diem_theo_he_so = math.ceil(diem_khoi_dau * (he_so_gap ** so_tay_thua_lien_tiep))
        diem_de_xuat = max(diem_khoi_dau, diem_can_go, diem_theo_he_so)
        che_do_tay = f"Gỡ lỗ tay thua #{so_tay_thua_lien_tiep}"

    # Khống chế trần vốn tối đa mỗi tay để giữ an toàn vốn gốc
    ngan_sach_tay_toi_da = int(max(0, von_hien_tai) * (ty_le_von_toi_da_tay / 100.0))
    if chi_phi_1_diem_dan > 0 and ngan_sach_tay_toi_da >= chi_phi_1_diem_dan:
        diem_tran = max(diem_khoi_dau, ngan_sach_tay_toi_da // chi_phi_1_diem_dan)
        diem_thuc_te = min(diem_de_xuat, diem_tran)
    else:
        diem_thuc_te = diem_de_xuat

    goc_danh = diem_thuc_te * chi_phi_1_diem_dan
    tien_trung = diem_thuc_te * tien_trung_1_diem
    lai_neu_an = tien_trung - goc_danh

    return {
        "diem_so": diem_thuc_te,
        "goc_danh": goc_danh,
        "tien_trung": tien_trung,
        "lai_neu_an": lai_neu_an,
        "che_do_tay": che_do_tay,
    }


def backtest_cau_95(
    ds_5so: list[str],
    vi_tri_chon: list[int],
    che_do_bong: str,
    so_luong_dan: int,
    nguong_ty_le: float,
    yeu_cau_an_thong: bool,
    cho_phep_du_phong: bool,
    gia_1_diem: int,
    tien_trung_1_diem: int,
    diem_khoi_dau: int,
    he_so_gap: float,
    lai_bu_toi_thieu: int,
    ty_le_von_toi_da_tay: float,
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
    bo_qua_cnt = 0

    von_hien_tai = von_ban_dau
    lo_don_hien_tai = 0
    so_tay_thua_lien_tiep = 0
    tong_goc_da_danh = 0

    for idx in range(2, len(ds_5so) - 1):
        lich_su_toi_ky = ds_5so[: idx + 1]
        _, tin_hieu_ky, _ = loc_cau_dat_chuan_95(
            lich_su_toi_ky,
            vi_tri_chon=vi_tri_chon,
            che_do_bong=che_do_bong,
            max_tien=8,
            max_lui=8,
            nguong_ty_le=nguong_ty_le,
            yeu_cau_an_thong=yeu_cau_an_thong,
            cho_phep_du_phong=cho_phep_du_phong,
        )
        _, dan_ky = cham_diem_siet_dan(tin_hieu_ky, so_luong_dan)
        ky_label = f"#{idx + 2} ({ds_5so[idx + 1]})"
        de_ky_sau = ds_5so[idx + 1][-2:]

        if not dan_ky:
            bo_qua_cnt += 1
            rows.append({
                "Kỳ KQ": ky_label,
                "Đề": de_ky_sau,
                "Điểm/số": 0,
                "Loại tay": f"Nghỉ (<{nguong_ty_le:.0f}%)",
                "Vốn tay": "0đ",
                "Tiền trúng": "0đ",
                "Lãi/Lỗ tay": "+0đ",
                "Lãi/Lỗ lũy kế": f"{von_hien_tai - von_ban_dau:+,}đ",
                "Trạng thái": "NGHỈ",
            })
            continue

        plan = tinh_diem_go_reset(
            so_luong_so=len(dan_ky),
            lo_don_hien_tai=lo_don_hien_tai,
            so_tay_thua_lien_tiep=so_tay_thua_lien_tiep,
            von_hien_tai=von_hien_tai,
            gia_1_diem=gia_1_diem,
            tien_trung_1_diem=tien_trung_1_diem,
            diem_khoi_dau=diem_khoi_dau,
            he_so_gap=he_so_gap,
            lai_bu_toi_thieu=lai_bu_toi_thieu,
            ty_le_von_toi_da_tay=ty_le_von_toi_da_tay,
        )

        goc_tay = plan["goc_danh"]
        tong_goc_da_danh += goc_tay
        von_truoc_tay = von_hien_tai
        is_an = de_ky_sau in set(dan_ky)

        if is_an:
            an_cnt += 1
            streak_cur += 1
            if streak_cur > streak_max:
                streak_max = streak_cur
            tien_trung_tay = plan["tien_trung"]
            lai_lo_tay = tien_trung_tay - goc_tay
            von_hien_tai = von_truoc_tay - goc_tay + tien_trung_tay
            # Đã thắng -> reset lỗ dồn & số tay thua liên tiếp để tay sau về mức khởi đầu
            lo_don_hien_tai = 0
            so_tay_thua_lien_tiep = 0
        else:
            truot_cnt += 1
            streak_cur = 0
            tien_trung_tay = 0
            lai_lo_tay = -goc_tay
            von_hien_tai = von_truoc_tay - goc_tay
            lo_don_hien_tai += goc_tay
            so_tay_thua_lien_tiep += 1

        lai_lo_luy_ke = von_hien_tai - von_ban_dau
        dat_moc_chot = lai_lo_luy_ke >= moc_chot_lai

        rows.append({
            "Kỳ KQ": ky_label,
            "Đề": de_ky_sau,
            "Điểm/số": plan["diem_so"],
            "Loại tay": plan["che_do_tay"],
            "Vốn tay": f"{goc_tay:,}đ",
            "Tiền trúng": f"{tien_trung_tay:,}đ",
            "Lãi/Lỗ tay": f"{lai_lo_tay:+,}đ",
            "Lãi/Lỗ lũy kế": f"{lai_lo_luy_ke:+,}đ",
            "Trạng thái": "ĂN (Reset gốc)" if is_an else "TRƯỢT",
        })

        bang_von_rows.append({
            "Kỳ KQ": ky_label,
            "Vốn trước tay": f"{von_truoc_tay:,}đ",
            "Gốc đánh": f"{goc_tay:,}đ",
            "Lỗ dồn": f"{lo_don_hien_tai:,}đ",
            "Tổng gốc đã đánh": f"{tong_goc_da_danh:,}đ",
            "Vốn còn lại": f"{von_hien_tai:,}đ",
        })

        bang_chot_lai_rows.append({
            "Kỳ KQ": ky_label,
            "Kết quả": "ĂN" if is_an else "TRƯỢT",
            "Lãi/Lỗ tay": f"{lai_lo_tay:+,}đ",
            "Lãi/Lỗ lũy kế": f"{lai_lo_luy_ke:+,}đ",
            "Mốc chốt lãi": f"{moc_chot_lai:,}đ",
            "Chốt lãi": "ĐẠT MỐC CHỐT" if dat_moc_chot else "Chưa đạt",
        })

    _, tin_hieu_cuoi, _ = loc_cau_dat_chuan_95(
        ds_5so,
        vi_tri_chon=vi_tri_chon,
        che_do_bong=che_do_bong,
        max_tien=8,
        max_lui=8,
        nguong_ty_le=nguong_ty_le,
        yeu_cau_an_thong=yeu_cau_an_thong,
        cho_phep_du_phong=cho_phep_du_phong,
    )
    _, dan_cuoi = cham_diem_siet_dan(tin_hieu_cuoi, so_luong_dan)

    ke_hoach_next = tinh_diem_go_reset(
        so_luong_so=len(dan_cuoi),
        lo_don_hien_tai=lo_don_hien_tai,
        so_tay_thua_lien_tiep=so_tay_thua_lien_tiep,
        von_hien_tai=von_hien_tai,
        gia_1_diem=gia_1_diem,
        tien_trung_1_diem=tien_trung_1_diem,
        diem_khoi_dau=diem_khoi_dau,
        he_so_gap=he_so_gap,
        lai_bu_toi_thieu=lai_bu_toi_thieu,
        ty_le_von_toi_da_tay=ty_le_von_toi_da_tay,
    )

    tong_tay_danh = an_cnt + truot_cnt
    ty_le_an = round((an_cnt / tong_tay_danh) * 100, 2) if tong_tay_danh else 0.0
    lai_lo_luy_ke_cuoi = von_hien_tai - von_ban_dau

    tom_tat = {
        "Số lần ĂN": an_cnt,
        "Số lần TRƯỢT": truot_cnt,
        "Số kỳ nghỉ": bo_qua_cnt,
        "Tỷ lệ ĂN (%)": ty_le_an,
        "Ăn thông max": streak_max,
        "Lãi/Lỗ tích lũy": lai_lo_luy_ke_cuoi,
        "Vốn hiện tại": von_hien_tai,
        "Tổng gốc đã đánh": tong_goc_da_danh,
        "Đạt mốc chốt lãi": lai_lo_luy_ke_cuoi >= moc_chot_lai,
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
st.title("🎯 Soi Cầu GĐB 5 Số - Gỡ Khi Thua & Thắng Reset Về Gốc")

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
            height=110,
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
    st.warning("Cần ít nhất 4 kỳ GĐB để đánh giá cầu và kiểm tra lịch sử.")
    st.stop()

c1, c2, c3, c4 = st.columns([2, 1.5, 1.3, 1.2])
with c1:
    vi_tri_chon = st.multiselect(
        "Vị trí xét (VT1..VT5)",
        options=[1, 2, 3, 4, 5],
        default=[1, 2, 3, 4, 5],
        format_func=lambda x: f"VT{x}",
    )
with c2:
    nguong_ty_le = float(
        st.slider("Tỷ lệ ăn tối thiểu (%)", min_value=50.0, max_value=100.0, value=95.0, step=1.0)
    )
with c3:
    che_do_bong = st.selectbox("Bóng", ["Không", "Bóng dương", "Bóng âm"])
with c4:
    so_luong_dan = int(st.selectbox("Dàn số", [55, 65, 75], index=1))

opt1, opt2 = st.columns(2)
with opt1:
    yeu_cau_an_thong = st.checkbox("Chỉ lấy cầu đang ăn thông (Streak hiện tại ≥ 1)", value=True)
with opt2:
    cho_phep_du_phong = st.checkbox(
        "Cho phép lấy dự phòng top cao nhất nếu chưa có cầu ≥ ngưỡng",
        value=True,
    )

st.markdown("### 💰 Cấu Hình Vào Tiền: Thua Nâng Gỡ Lãi - Thắng Reset Về Khởi Đầu")
v1, v2, v3, v4 = st.columns(4)
with v1:
    von_ban_dau = int(
        st.number_input("Vốn ban đầu (đ)", min_value=1000, max_value=100_000_000_000, value=5_000_000, step=100_000)
    )
with v2:
    gia_1_diem = int(
        st.number_input("Giá 1 điểm / số (đ)", min_value=100, max_value=10_000_000, value=1000, step=100)
    )
with v3:
    tien_trung_1_diem = int(
        st.number_input("Tiền trúng 1 điểm (đ)", min_value=1000, max_value=500_000_000, value=99900, step=100)
    )
with v4:
    diem_khoi_dau = int(
        st.number_input("Điểm khởi đầu (vd: 5)", min_value=1, max_value=10000, value=5, step=1)
    )

v5, v6, v7, v8 = st.columns(4)
with v5:
    he_so_gap = float(
        st.number_input("Hệ số nhân khi thua", min_value=1.0, max_value=10.0, value=2.0, step=0.5)
    )
with v6:
    lai_bu_toi_thieu = int(
        st.number_input("Lãi cộng thêm khi gỡ (đ)", min_value=0, max_value=100_000_000, value=10000, step=1000)
    )
with v7:
    ty_le_von_toi_da_tay = float(
        st.slider("Trần vốn/tay (% vốn hiện tại)", min_value=10.0, max_value=100.0, value=50.0, step=5.0)
    )
with v8:
    moc_chot_lai = int(
        st.number_input("Mốc chốt lãi tổng (đ)", min_value=0, max_value=10_000_000_000, value=200000, step=10000)
    )

if not vi_tri_chon:
    st.warning("Vui lòng chọn ít nhất 1 vị trí.")
    st.stop()

df_dat_chuan, tin_hieu_chuan, du_phong_da_dung = loc_cau_dat_chuan_95(
    ds_5so=ds_5so,
    vi_tri_chon=sorted(vi_tri_chon),
    che_do_bong=che_do_bong,
    max_tien=8,
    max_lui=8,
    nguong_ty_le=nguong_ty_le,
    yeu_cau_an_thong=yeu_cau_an_thong,
    cho_phep_du_phong=cho_phep_du_phong,
)
df_diem, dan_chon = cham_diem_siet_dan(tin_hieu_chuan, so_luong_dan)

df_bt, df_von, df_chot_lai, tom_tat_bt, ke_hoach_next = backtest_cau_95(
    ds_5so=ds_5so,
    vi_tri_chon=sorted(vi_tri_chon),
    che_do_bong=che_do_bong,
    so_luong_dan=so_luong_dan,
    nguong_ty_le=nguong_ty_le,
    yeu_cau_an_thong=yeu_cau_an_thong,
    cho_phep_du_phong=cho_phep_du_phong,
    gia_1_diem=gia_1_diem,
    tien_trung_1_diem=tien_trung_1_diem,
    diem_khoi_dau=diem_khoi_dau,
    he_so_gap=he_so_gap,
    lai_bu_toi_thieu=lai_bu_toi_thieu,
    ty_le_von_toi_da_tay=ty_le_von_toi_da_tay,
    von_ban_dau=von_ban_dau,
    moc_chot_lai=moc_chot_lai,
)

if du_phong_da_dung:
    st.info(
        f"Chưa có cầu nào đạt **≥ {nguong_ty_le:.0f}%**; đang dùng **5 cầu dự phòng cao nhất** (bạn có thể tắt tùy chọn dự phòng nếu chỉ muốn đánh khi đủ ngưỡng)."
    )
elif tin_hieu_chuan:
    st.success(
        f"✅ Đang dùng **{len(tin_hieu_chuan)}** cầu đạt **≥ {nguong_ty_le:.0f}%** để tạo dàn **{len(dan_chon)} số**."
    )
else:
    st.warning(f"⏸️ Hiện chưa có cầu nào đạt **≥ {nguong_ty_le:.0f}%**.")

tab1, tab2, tab3, tab4 = st.tabs([
    f"🎲 Dàn {len(dan_chon)} Số & Kỳ Tới",
    "💼 Bảng Vốn & Chốt Lãi",
    f"🏆 Cầu ≥ {nguong_ty_le:.0f}%",
    "📜 Lịch Sử ĂN / TRƯỢT",
])

with tab1:
    if dan_chon:
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

        render_copy_button(chuoi_copy, label=f"📋 COPY DÀN {len(dan_chon)} SỐ", key_suffix="rst")
        render_dan_co_dong(dan_chon, delimiter=delim)

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Điểm/số kỳ tới", f"{ke_hoach_next['diem_so']} điểm")
        k2.metric("Gốc đánh kỳ tới", f"{ke_hoach_next['goc_danh']:,}đ")
        k3.metric("Tiền trúng (nếu ăn)", f"{ke_hoach_next['tien_trung']:,}đ")
        k4.metric("Lãi ròng nếu ăn", f"{ke_hoach_next['lai_neu_an']:+,}đ")
        st.caption(f"Trạng thái kế hoạch kỳ tới: **{ke_hoach_next['che_do_tay']}**")
    else:
        st.info("Chưa có dàn số để hiển thị.")

with tab2:
    t1, t2, t3, t4 = st.columns(4)
    t1.metric("Vốn ban đầu", f"{von_ban_dau:,}đ")
    t2.metric("Vốn còn lại", f"{tom_tat_bt['Vốn hiện tại']:,}đ")
    t3.metric("Lãi/Lỗ tích lũy", f"{tom_tat_bt['Lãi/Lỗ tích lũy']:+,}đ")
    t4.metric(
        "Chốt lãi",
        "ĐẠT MỐC CHỐT" if tom_tat_bt["Đạt mốc chốt lãi"] else "Chưa đạt",
    )

    st.subheader("💼 Bảng Vốn")
    st.dataframe(df_von, use_container_width=True, hide_index=True)

    st.subheader("💵 Bảng Chốt Lãi")
    st.dataframe(df_chot_lai, use_container_width=True, hide_index=True)

with tab3:
    if not df_dat_chuan.empty:
        st.dataframe(df_dat_chuan, use_container_width=True, hide_index=True)
    else:
        st.info(f"Không có cầu nào đạt tỷ lệ ăn ≥ {nguong_ty_le:.0f}%.")

with tab4:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Số lần ĂN", tom_tat_bt["Số lần ĂN"])
    m2.metric("Số lần TRƯỢT", tom_tat_bt["Số lần TRƯỢT"])
    m3.metric("Tỷ lệ ĂN", f"{tom_tat_bt['Tỷ lệ ĂN (%)']}%")
    m4.metric("Ăn thông max", tom_tat_bt["Ăn thông max"])

    st.dataframe(df_bt, use_container_width=True, hide_index=True)