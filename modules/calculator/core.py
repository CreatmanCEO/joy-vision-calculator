# core/calculator.py
"""
Точный расчёт комплектующих для систем безрамного остекления
Системы: Slider L, Slider X, Line, Zig-Zag
"""

def calculate_slider_l(width, height, panels, opening="влево", 
                       left_edge="боковой профиль", right_edge="боковой профиль",
                       handle_type="круглая", handle_count=2, 
                       latch_count=2, glass_thickness=10,
                       seal_type="светопрозрачный",
                       handle_height=1000,
                       painting=False, ral_color=None, custom_colors=False):
    """
    Расчёт параллельно-сдвижной системы Slider L
    
    Параметры:
        width: ширина проёма (мм)
        height: высота проёма (мм)
        panels: количество створок
        opening: тип открывания ("влево", "вправо", "от центра")
        left_edge/right_edge: тип края ("боковой профиль", "без профиля", "стык 90 градусов")
        handle_type: тип ручки ("круглая", "прозрачная")
        handle_count: количество ручек (1, 2, 4)
        latch_count: количество защелок (0, 1, 2, 4)
        glass_thickness: толщина стекла (мм), по умолчанию 10 мм (закаленное)
        seal_type: тип межстворочного уплотнения ("светопрозрачный", "щеточный")
        handle_height: высота от пола до ручки (мм)
        painting: нужна ли покраска
        ral_color: цвет по карте RAL
        custom_colors: задать цвет вручную для каждого профиля
    """
    
    # ===== 1. ОПРЕДЕЛЕНИЕ ТИПА СИСТЕМЫ (3 или 5 дорожек) =====
    is_center_opening = opening == "от центра"
    
    if is_center_opening:
        if 4 <= panels <= 6:
            track_type = "3 дорожки"
            track_count = 3
            top_profile_code = "S-010"
            top_profile_height = 48
            bottom_profile_code = "SL-110"
            glass_height = height - 105
        elif 8 <= panels <= 10:
            track_type = "5 дорожек"
            track_count = 5
            top_profile_code = "S-020"
            top_profile_height = 52
            bottom_profile_code = "SL-120"
            glass_height = height - 110
        else:
            raise ValueError(f"Для открывания '{opening}' допустимо 4-6 створок (3 дорожки) или 8-10 створок (5 дорожек)")
    else:
        if 2 <= panels <= 3:
            track_type = "3 дорожки"
            track_count = 3
            top_profile_code = "S-010"
            top_profile_height = 48
            bottom_profile_code = "SL-110"
            glass_height = height - 105
        elif 4 <= panels <= 5:
            track_type = "5 дорожек"
            track_count = 5
            top_profile_code = "S-020"
            top_profile_height = 52
            bottom_profile_code = "SL-120"
            glass_height = height - 110
        else:
            raise ValueError(f"Для открывания '{opening}' допустимо 2-3 створки (3 дорожки) или 4-5 створок (5 дорожек)")
    
    # ===== 2. РАСЧЁТ ШИРИНЫ СТЕКЛА =====
    side_profiles_count = 0
    if left_edge == "боковой профиль":
        side_profiles_count += 1
    if right_edge == "боковой профиль":
        side_profiles_count += 1
    
    gap_with_profile = 10
    gap_without_profile = 6
    total_gap = side_profiles_count * gap_with_profile + (2 - side_profiles_count) * gap_without_profile
    
    if is_center_opening:
        overlaps_count = panels - 2
        center_gap = 20
        glass_width = (width - total_gap + overlaps_count * 15 - center_gap) / panels
    else:
        overlaps_count = panels - 1
        center_gap = 0
        glass_width = (width - total_gap + overlaps_count * 15) / panels
    
    glass_width = round((glass_width + 0.05) // 0.1 * 0.1, 1)
    
    # ===== 3. РАСЧЁТ МАССЫ СТВОРКИ =====
    glass_area = (glass_width / 1000) * (glass_height / 1000)
    glass_weight_kg = glass_area * (glass_thickness * 2.5)
    
    # ===== 4. ПРОФИЛИ С ЗАПАСОМ НА РЕЗКУ =====
    top_profile_length = width
    top_profile_cut_waste = 75 + 5 * 0
    top_profile_total = top_profile_length + top_profile_cut_waste
    
    bottom_profile_length = width
    bottom_profile_height = 7
    bottom_profile_cut_waste = 75 + 5 * 0
    bottom_profile_total = bottom_profile_length + bottom_profile_cut_waste
    
    side_profile_length = height - top_profile_height - bottom_profile_height
    side_profile_cut_waste = 75 + 5 * 1
    side_profile_total_per_piece = side_profile_length + side_profile_cut_waste
    side_profile_qty = 2
    
    sash_profile_length_per_panel = glass_width
    sash_profile_cuts = panels - 1
    sash_profile_cut_waste = 75 + 5 * sash_profile_cuts
    sash_profile_total = sash_profile_length_per_panel * panels + sash_profile_cut_waste
    
    # ===== 5. ЗАГЛУШКИ =====
    side_plugs = 0
    middle_plugs = 0
    
    # Примыкание к стенам
    if left_edge == "боковой профиль":
        side_plugs += 1
    else:
        middle_plugs += 1
    
    if right_edge == "боковой профиль":
        side_plugs += 1
    else:
        middle_plugs += 1
    
    # Стыки между створками
    if is_center_opening:
        left_half_panels = panels // 2
        
        if left_half_panels > 1:
            middle_plugs += 1
            if left_half_panels > 2:
                middle_plugs += (left_half_panels - 2) * 2
            middle_plugs += 1
        
        side_plugs += 2
        
        right_half_panels = panels - left_half_panels
        
        if right_half_panels > 1:
            middle_plugs += 1
            if right_half_panels > 2:
                middle_plugs += (right_half_panels - 2) * 2
            middle_plugs += 1
    
    else:
        middle_plugs += (panels - 1) * 2
    
    total_plugs = side_plugs + middle_plugs
    
    # ===== 6. ДЕМПФЕРЫ =====
    dampers_qty = middle_plugs
    
    # ===== 7. РОЛИКИ =====
    rollers_base = panels * 2
    rollers_extra = panels * 2 if glass_weight_kg > 90 else 0
    rollers_total = rollers_base + rollers_extra
    
    # ===== 8. РУЧКИ И ЗАДВИЖКИ =====
    handle_code = "S-040" if handle_type == "круглая" else "S-050"
    handles_qty = handle_count
    latches_qty = latch_count
    
    # ===== 9. УПЛОТНИТЕЛИ =====
    seal_top_length_m = (top_profile_length * track_count * 2) / 1000
    seal_side_length_m = (side_profile_length * 2 * 2) / 1000
    
    if is_center_opening:
        seal_interpanel_length_mm = glass_height * (panels - 2)
        magnetic_seal_length_m = glass_height / 1000
    else:
        seal_interpanel_length_mm = glass_height * (panels - 1)
        magnetic_seal_length_m = 0
    
    if seal_type == "светопрозрачный":
        aa060_pieces = -(-seal_interpanel_length_mm // 3000)
        aa070_pieces = -(- (glass_height * 2) // 3000)
        aa071_pieces = 0
        aa041_length_m = 0
        aa060_total_m = aa060_pieces * 3
        aa070_total_m = aa070_pieces * 3
    else:  # "щеточный"
        aa071_pieces = -(-seal_interpanel_length_mm // 3000)
        aa041_length_m = seal_interpanel_length_mm / 1000
        aa060_pieces = 0
        aa070_pieces = 0
        aa060_total_m = 0
        aa070_total_m = 0
    
    # ===== 10. КРЕПЁЖ =====
    top_screws = 2
    remaining_top = width - 200
    if remaining_top > 0:
        top_screws += -(-remaining_top // 1000)
    
    bottom_screws = 2
    remaining_bottom = width - 200
    if remaining_bottom > 0:
        bottom_screws += -(-remaining_bottom // 700)
    
    plug_screws = total_plugs * 2
    latch_screws = latches_qty * 2
    
    # ===== 11. РАСЧЁТ КЛЕЯ И АКТИВАТОРА =====
    # Для слайдера: клей наносится на 2 стороны створочника (сверху и снизу)
    glue_per_panel_m = (glass_width / 1000) * 2
    total_glue_length_m = glue_per_panel_m * panels
    
    # 1 туба клея + 1 банка активатора хватает на 18 метров клеевого шва
    glue_tubes = max(1, int((total_glue_length_m + 17.999) // 18))  # округление вверх, минимум 1
    activator_bottles = glue_tubes
    
    # ===== ФОРМИРОВАНИЕ РЕЗУЛЬТАТА =====
    result = {
        "system_info": {
            "type": "Slider L",
            "track_type": track_type,
            "track_count": track_count,
            "opening": opening,
            "panels": panels,
            "left_edge": left_edge,
            "right_edge": right_edge,
            "width_mm": width,
            "height_mm": height,
            "glass_width_mm": glass_width,
            "glass_height_mm": glass_height,
            "glass_weight_kg": round(glass_weight_kg, 1),
            "glass_thickness_mm": glass_thickness,
            "needs_extra_rollers": glass_weight_kg > 90,
            "side_profiles_count": side_profiles_count,
            "overlaps_count": overlaps_count,
            "center_gap_mm": center_gap if is_center_opening else 0,
            "handle_height_mm": handle_height,
            "painting": painting,
            "ral_color": ral_color,
            "custom_colors": custom_colors
        },
        "profiles": [
            {
                "code": top_profile_code,
                "name": f"Верхний профиль {track_count} дорожки",
                "length_per_piece_mm": top_profile_length,
                "cut_waste_mm": top_profile_cut_waste,
                "total_with_waste_mm": top_profile_total,
                "qty": 1,
                "total_m": round(top_profile_total / 1000, 3)
            },
            {
                "code": bottom_profile_code,
                "name": f"Нижний опорный профиль L {track_count} дорожки",
                "length_per_piece_mm": bottom_profile_length,
                "cut_waste_mm": bottom_profile_cut_waste,
                "total_with_waste_mm": bottom_profile_total,
                "qty": 1,
                "total_m": round(bottom_profile_total / 1000, 3)
            },
            {
                "code": "S-030",
                "name": "Боковой профиль",
                "length_per_piece_mm": side_profile_length,
                "cut_waste_mm": side_profile_cut_waste,
                "total_with_waste_mm": side_profile_total_per_piece,
                "qty": side_profile_qty,
                "total_m": round(side_profile_total_per_piece / 1000 * side_profile_qty, 3)
            },
            {
                "code": "SL-130",
                "name": "Створочный профиль",
                "length_per_piece_mm": round(sash_profile_length_per_panel, 1),
                "cut_waste_mm": sash_profile_cut_waste,
                "total_with_waste_mm": round(sash_profile_total, 1),
                "qty": panels,
                "total_m": round(sash_profile_total / 1000, 3),
                "note": f"Резов: {sash_profile_cuts}, запас: {sash_profile_cut_waste} мм"
            }
        ],
        "hardware": [
            {
                "code": "SL-140-0",
                "name": "Заглушка боковая",
                "qty": side_plugs
            },
            {
                "code": "SL-140-2",
                "name": "Заглушка створочная двусторонняя",
                "qty": middle_plugs
            },
            {
                "code": "S-080",
                "name": "Демпфер заглушки с кольцом",
                "qty": dampers_qty
            },
            {
                "code": "SL-150",
                "name": "Роликовая каретка L",
                "qty": rollers_total,
                "note": f"Базово: {rollers_base} шт" + (f", +{rollers_extra} доп." if rollers_extra else "")
            },
            {
                "code": handle_code,
                "name": f"Ручка {handle_type}",
                "qty": handles_qty
            },
            {
                "code": "SL-160",
                "name": "Задвижка нижняя L",
                "qty": latches_qty
            }
        ],
        "seals": [
            {
                "code": "AA-030",
                "name": "Уплотнитель щеточный 5х4 (верхний профиль)",
                "type": "погонные метры",
                "total_m": round(seal_top_length_m, 3)
            },
            {
                "code": "AA-040",
                "name": "Уплотнитель щеточный 5х9 (боковой профиль)",
                "type": "погонные метры",
                "total_m": round(seal_side_length_m, 3)
            }
        ],
        "interpanel_seals": []
    }
    
    # Межстворочные уплотнители
    if seal_type == "светопрозрачный":
        result["interpanel_seals"].extend([
            {
                "code": "AA-060",
                "name": "Уплотнитель светопрозрачный F-типа",
                "type": "шт",
                "pieces": int(aa060_pieces),
                "total_m": round(aa060_total_m, 3)
            },
            {
                "code": "AA-070",
                "name": "Уплотнитель светопрозрачный D-типа (крайние створки)",
                "type": "шт",
                "pieces": int(aa070_pieces),
                "total_m": round(aa070_total_m, 3)
            }
        ])
    else:  # щеточный
        result["interpanel_seals"].extend([
            {
                "code": "AA-071",
                "name": "Уплотнитель светопрозрачный под щетку",
                "type": "шт",
                "pieces": int(aa071_pieces),
                "total_m": round(aa071_pieces * 3, 3)
            },
            {
                "code": "AA-041",
                "name": "Уплотнитель щеточный 5х12 с клеевой основой",
                "type": "погонные метры",
                "total_m": round(aa041_length_m, 3)
            }
        ])
    
    # Магнитный уплотнитель для центрального стыка
    if is_center_opening:
        result["interpanel_seals"].append({
            "code": "AA-020",
            "name": "Магнитный уплотнитель (центральный стык)",
            "type": "погонные метры",
            "total_m": round(magnetic_seal_length_m, 3)
        })
    
    # Расходники и крепёж
    result["consumables"] = [
        {
            "code": "AA-110",
            "name": "Активатор (50 мл)",
            "qty": int(activator_bottles),
            "unit": "шт"
        },
        {
            "code": "AA-120",
            "name": "Клей (уп. колбаса)",
            "qty": int(glue_tubes),
            "unit": "уп"
        }
    ]
    
    result["fasteners"] = [
        {
            "code": "AA-200",
            "name": "Саморез для опорного профиля (верх)",
            "qty": top_screws,
            "unit": "шт"
        },
        {
            "code": "AA-200",
            "name": "Саморез для опорного профиля (низ)",
            "qty": bottom_screws,
            "unit": "шт"
        },
        {
            "code": "AA-201",
            "name": "Саморез 3.5х20 для крепления заглушек",
            "qty": plug_screws,
            "unit": "шт"
        },
        {
            "code": "AA-202",
            "name": "Саморез с прессшайбой 4.2х25 для задвижек",
            "qty": latch_screws,
            "unit": "шт"
        }
    ]
    
    # Итоги
    result["summary"] = {
        "total_profiles_m": round(
            (top_profile_total + bottom_profile_total + 
             side_profile_total_per_piece * side_profile_qty + 
             sash_profile_total) / 1000, 3
        ),
        "total_seals_m": round(
            (seal_top_length_m * 1000 + seal_side_length_m * 1000 + seal_interpanel_length_mm + magnetic_seal_length_m * 1000) / 1000, 3
        ),
        "total_hardware_items": (
            side_plugs + middle_plugs + dampers_qty + 
            rollers_total + handles_qty + latches_qty
        ),
        "plug_distribution": f"Боковые: {side_plugs}, Двусторонние: {middle_plugs}, Всего: {total_plugs} (должно быть {panels * 2})",
        "glue_info": f"Клей: {int(glue_tubes)} туб, Активатор: {int(activator_bottles)} банок (на {total_glue_length_m:.1f} м шва)"
    }
    
    return result


def calculate_slider_x(width, height, panels, opening="влево", 
                       left_edge="боковой профиль", right_edge="боковой профиль",
                       handle_type="круглая", handle_count=2, 
                       glass_thickness=10, seal_type="светопрозрачный",
                       handle_height=1000,
                       painting=False, ral_color=None, custom_colors=False):
    """
    Расчёт параллельно-сдвижной системы Slider X
    
    Параметры аналогичны Slider L
    """
    
    # ===== 1. ОПРЕДЕЛЕНИЕ ТИПА СИСТЕМЫ (3 или 5 дорожек) =====
    is_center_opening = opening == "от центра"
    
    if is_center_opening:
        if 4 <= panels <= 6:
            track_type = "3 дорожки"
            track_count = 3
            top_profile_code = "S-010"
            top_profile_height = 48
            bottom_profile_code = "SX-110"
            glass_height = height - 100
        elif 8 <= panels <= 10:
            track_type = "5 дорожек"
            track_count = 5
            top_profile_code = "S-020"
            top_profile_height = 52
            bottom_profile_code = "SX-120"
            glass_height = height - 105
        else:
            raise ValueError(f"Для открывания '{opening}' допустимо 4-6 створок (3 дорожки) или 8-10 створок (5 дорожек)")
    else:
        if 2 <= panels <= 3:
            track_type = "3 дорожки"
            track_count = 3
            top_profile_code = "S-010"
            top_profile_height = 48
            bottom_profile_code = "SX-110"
            glass_height = height - 100
        elif 4 <= panels <= 5:
            track_type = "5 дорожек"
            track_count = 5
            top_profile_code = "S-020"
            top_profile_height = 52
            bottom_profile_code = "SX-120"
            glass_height = height - 105
        else:
            raise ValueError(f"Для открывания '{opening}' допустимо 2-3 створки (3 дорожки) или 4-5 створок (5 дорожек)")
    
    # ===== 2. РАСЧЁТ ШИРИНЫ СТЕКЛА =====
    side_profiles_count = 0
    if left_edge == "боковой профиль":
        side_profiles_count += 1
    if right_edge == "боковой профиль":
        side_profiles_count += 1
    
    gap_with_profile = 10
    gap_without_profile = 6
    total_gap = side_profiles_count * gap_with_profile + (2 - side_profiles_count) * gap_without_profile
    
    if is_center_opening:
        overlaps_count = panels - 2
        center_gap = 20
        glass_width = (width - total_gap + overlaps_count * 15 - center_gap) / panels
    else:
        overlaps_count = panels - 1
        center_gap = 0
        glass_width = (width - total_gap + overlaps_count * 15) / panels
    
    glass_width = round((glass_width + 0.05) // 0.1 * 0.1, 1)
    
    # ===== 3. РАСЧЁТ МАССЫ СТВОРКИ =====
    glass_area = (glass_width / 1000) * (glass_height / 1000)
    glass_weight_kg = glass_area * (glass_thickness * 2.5)
    
    # ===== 4. ПРОФИЛИ С ЗАПАСОМ НА РЕЗКУ =====
    top_profile_length = width
    top_profile_cut_waste = 75 + 5 * 0
    top_profile_total = top_profile_length + top_profile_cut_waste
    
    bottom_profile_length = width
    bottom_profile_height = 21
    bottom_profile_cut_waste = 75 + 5 * 0
    bottom_profile_total = bottom_profile_length + bottom_profile_cut_waste
    
    side_profile_length = height - top_profile_height - bottom_profile_height
    side_profile_cut_waste = 75 + 5 * 1
    side_profile_total_per_piece = side_profile_length + side_profile_cut_waste
    side_profile_qty = 2
    
    sash_profile_length_per_panel = glass_width
    sash_profile_cuts = panels - 1
    sash_profile_cut_waste = 75 + 5 * sash_profile_cuts
    sash_profile_total = sash_profile_length_per_panel * panels + sash_profile_cut_waste
    
    # ===== 5. ЗАГЛУШКИ (ТАКАЯ ЖЕ ЛОГИКА КАК У SLIDER L) =====
    side_plugs = 0
    middle_plugs = 0
    
    if left_edge == "боковой профиль":
        side_plugs += 1
    else:
        middle_plugs += 1
    
    if right_edge == "боковой профиль":
        side_plugs += 1
    else:
        middle_plugs += 1
    
    if is_center_opening:
        left_half_panels = panels // 2
        
        if left_half_panels > 1:
            middle_plugs += 1
            if left_half_panels > 2:
                middle_plugs += (left_half_panels - 2) * 2
            middle_plugs += 1
        
        side_plugs += 2
        
        right_half_panels = panels - left_half_panels
        
        if right_half_panels > 1:
            middle_plugs += 1
            if right_half_panels > 2:
                middle_plugs += (right_half_panels - 2) * 2
            middle_plugs += 1
    
    else:
        middle_plugs += (panels - 1) * 2
    
    total_plugs = side_plugs + middle_plugs
    
    # ===== 6. ДЕМПФЕРЫ =====
    dampers_qty = middle_plugs
    
    # ===== 7. РОЛИКИ =====
    rollers_base = panels * 2
    rollers_extra = panels * 2 if glass_weight_kg > 100 else 0  # 100 кг вместо 90 кг
    rollers_total = rollers_base + rollers_extra
    
    # ===== 8. РУЧКИ =====
    handle_code = "S-040" if handle_type == "круглая" else "S-050"
    handles_qty = handle_count
    
    # ===== 9. ЗАДВИЖКИ =====
    if is_center_opening:
        if panels % 2 == 0:
            external_latches = 2
            internal_latches = 2
        else:
            external_latches = 1
            internal_latches = 2
    else:
        external_latches = 1
        internal_latches = 1
    
    # ===== 10. УПЛОТНИТЕЛИ =====
    seal_top_length_m = (top_profile_length * track_count * 2) / 1000
    seal_side_length_m = (side_profile_length * 2 * 2) / 1000
    
    if is_center_opening:
        seal_interpanel_length_mm = glass_height * (panels - 2)
        magnetic_seal_length_m = glass_height / 1000
    else:
        seal_interpanel_length_mm = glass_height * (panels - 1)
        magnetic_seal_length_m = 0
    
    if seal_type == "светопрозрачный":
        aa060_pieces = -(-seal_interpanel_length_mm // 3000)
        aa070_pieces = -(- (glass_height * 2) // 3000)
        aa071_pieces = 0
        aa041_length_m = 0
        aa060_total_m = aa060_pieces * 3
        aa070_total_m = aa070_pieces * 3
    else:  # "щеточный"
        aa071_pieces = -(-seal_interpanel_length_mm // 3000)
        aa041_length_m = seal_interpanel_length_mm / 1000
        aa060_pieces = 0
        aa070_pieces = 0
        aa060_total_m = 0
        aa070_total_m = 0
    
    # ===== 11. КРЕПЁЖ =====
    top_screws = 2
    remaining_top = width - 200
    if remaining_top > 0:
        top_screws += -(-remaining_top // 1000)
    
    bottom_screws = 2
    remaining_bottom = width - 200
    if remaining_bottom > 0:
        bottom_screws += -(-remaining_bottom // 700)
    
    plug_screws = total_plugs * 2
    roller_screws = rollers_total * 2
    latch_screws = (external_latches + internal_latches) * 2
    
    # ===== 12. РАСЧЁТ КЛЕЯ И АКТИВАТОРА =====
    # Для слайдера: клей наносится на 2 стороны створочника (сверху и снизу)
    glue_per_panel_m = (glass_width / 1000) * 2
    total_glue_length_m = glue_per_panel_m * panels
    
    glue_tubes = max(1, int((total_glue_length_m + 17.999) // 18))
    activator_bottles = glue_tubes
    
    # ===== ФОРМИРОВАНИЕ РЕЗУЛЬТАТА =====
    result = {
        "system_info": {
            "type": "Slider X",
            "track_type": track_type,
            "track_count": track_count,
            "opening": opening,
            "panels": panels,
            "left_edge": left_edge,
            "right_edge": right_edge,
            "width_mm": width,
            "height_mm": height,
            "glass_width_mm": glass_width,
            "glass_height_mm": glass_height,
            "glass_weight_kg": round(glass_weight_kg, 1),
            "glass_thickness_mm": glass_thickness,
            "needs_extra_rollers": glass_weight_kg > 100,
            "side_profiles_count": side_profiles_count,
            "overlaps_count": overlaps_count,
            "center_gap_mm": center_gap if is_center_opening else 0,
            "handle_height_mm": handle_height,
            "painting": painting,
            "ral_color": ral_color,
            "custom_colors": custom_colors
        },
        "profiles": [
            {
                "code": top_profile_code,
                "name": f"Верхний профиль {track_count} дорожки",
                "length_per_piece_mm": top_profile_length,
                "cut_waste_mm": top_profile_cut_waste,
                "total_with_waste_mm": top_profile_total,
                "qty": 1,
                "total_m": round(top_profile_total / 1000, 3)
            },
            {
                "code": bottom_profile_code,
                "name": f"Нижний опорный профиль X {track_count} дорожки",
                "length_per_piece_mm": bottom_profile_length,
                "cut_waste_mm": bottom_profile_cut_waste,
                "total_with_waste_mm": bottom_profile_total,
                "qty": 1,
                "total_m": round(bottom_profile_total / 1000, 3)
            },
            {
                "code": "S-030",
                "name": "Боковой профиль",
                "length_per_piece_mm": side_profile_length,
                "cut_waste_mm": side_profile_cut_waste,
                "total_with_waste_mm": side_profile_total_per_piece,
                "qty": side_profile_qty,
                "total_m": round(side_profile_total_per_piece / 1000 * side_profile_qty, 3)
            },
            {
                "code": "SX-130",
                "name": "Створочный профиль",
                "length_per_piece_mm": round(sash_profile_length_per_panel, 1),
                "cut_waste_mm": sash_profile_cut_waste,
                "total_with_waste_mm": round(sash_profile_total, 1),
                "qty": panels,
                "total_m": round(sash_profile_total / 1000, 3),
                "note": f"Резов: {sash_profile_cuts}, запас: {sash_profile_cut_waste} мм"
            }
        ],
        "hardware": [
            {
                "code": "SX-140-0",
                "name": "Заглушка боковая",
                "qty": side_plugs
            },
            {
                "code": "SX-140-2",
                "name": "Заглушка створочная двусторонняя",
                "qty": middle_plugs
            },
            {
                "code": "S-080",
                "name": "Демпфер заглушки с кольцом",
                "qty": dampers_qty
            },
            {
                "code": "SX-150",
                "name": "Роликовая каретка X",
                "qty": rollers_total,
                "note": f"Базово: {rollers_base} шт" + (f", +{rollers_extra} доп." if rollers_extra else "")
            },
            {
                "code": handle_code,
                "name": f"Ручка {handle_type}",
                "qty": handles_qty
            },
            {
                "code": "SX-081",
                "name": "Задвижка нижняя X внешняя",
                "qty": external_latches,
                "note": "На центральные створки" if is_center_opening else "На крайнюю створку"
            },
            {
                "code": "SX-082",
                "name": "Задвижка нижняя X внутренняя",
                "qty": internal_latches,
                "note": "На крайние створки" if is_center_opening else "На крайнюю створку"
            }
        ],
        "seals": [
            {
                "code": "AA-030",
                "name": "Уплотнитель щеточный 5х4 (верхний профиль)",
                "type": "погонные метры",
                "total_m": round(seal_top_length_m, 3)
            },
            {
                "code": "AA-040",
                "name": "Уплотнитель щеточный 5х9 (боковой профиль)",
                "type": "погонные метры",
                "total_m": round(seal_side_length_m, 3)
            }
        ],
        "interpanel_seals": []
    }
    
    # Межстворочные уплотнители
    if seal_type == "светопрозрачный":
        result["interpanel_seals"].extend([
            {
                "code": "AA-060",
                "name": "Уплотнитель светопрозрачный F-типа",
                "type": "шт",
                "pieces": int(aa060_pieces),
                "total_m": round(aa060_total_m, 3)
            },
            {
                "code": "AA-070",
                "name": "Уплотнитель светопрозрачный D-типа (крайние створки)",
                "type": "шт",
                "pieces": int(aa070_pieces),
                "total_m": round(aa070_total_m, 3)
            }
        ])
    else:  # щеточный
        result["interpanel_seals"].extend([
            {
                "code": "AA-071",
                "name": "Уплотнитель светопрозрачный под щетку",
                "type": "шт",
                "pieces": int(aa071_pieces),
                "total_m": round(aa071_pieces * 3, 3)
            },
            {
                "code": "AA-041",
                "name": "Уплотнитель щеточный 5х12 с клеевой основой",
                "type": "погонные метры",
                "total_m": round(aa041_length_m, 3)
            }
        ])
    
    # Магнитный уплотнитель для центрального стыка
    if is_center_opening:
        result["interpanel_seals"].append({
            "code": "AA-020",
            "name": "Магнитный уплотнитель (центральный стык)",
            "type": "погонные метры",
            "total_m": round(magnetic_seal_length_m, 3)
        })
    
    # Расходники и крепёж
    result["consumables"] = [
        {
            "code": "AA-110",
            "name": "Активатор (50 мл)",
            "qty": int(activator_bottles),
            "unit": "шт"
        },
        {
            "code": "AA-120",
            "name": "Клей (уп. колбаса)",
            "qty": int(glue_tubes),
            "unit": "уп"
        }
    ]
    
    result["fasteners"] = [
        {
            "code": "AA-200",
            "name": "Саморез для опорного профиля (верх)",
            "qty": top_screws,
            "unit": "шт"
        },
        {
            "code": "AA-200",
            "name": "Саморез для опорного профиля (низ)",
            "qty": bottom_screws,
            "unit": "шт"
        },
        {
            "code": "AA-201",
            "name": "Саморез 3.5х20 для крепления заглушек",
            "qty": plug_screws,
            "unit": "шт"
        },
        {
            "code": "AA-203",
            "name": "Саморез с буром 3.9х22 для роликовых кареток",
            "qty": roller_screws,
            "unit": "шт"
        },
        {
            "code": "AA-204",
            "name": "Саморез 3х16 для задвижек X",
            "qty": latch_screws,
            "unit": "шт"
        }
    ]
    
    # Итоги
    result["summary"] = {
        "total_profiles_m": round(
            (top_profile_total + bottom_profile_total + 
             side_profile_total_per_piece * side_profile_qty + 
             sash_profile_total) / 1000, 3
        ),
        "total_seals_m": round(
            (seal_top_length_m * 1000 + seal_side_length_m * 1000 + seal_interpanel_length_mm + magnetic_seal_length_m * 1000) / 1000, 3
        ),
        "total_hardware_items": (
            side_plugs + middle_plugs + dampers_qty + 
            rollers_total + handles_qty + external_latches + internal_latches
        ),
        "plug_distribution": f"Боковые: {side_plugs}, Двусторонние: {middle_plugs}, Всего: {total_plugs} (должно быть {panels * 2})",
        "glue_info": f"Клей: {int(glue_tubes)} туб, Активатор: {int(activator_bottles)} банок (на {total_glue_length_m:.1f} м шва)"
    }
    
    return result


def calculate_jv_line(width, height, panels, 
                      opening="влево", 
                      left_edge="боковой профиль", 
                      right_edge="боковой профиль",
                      handle_type="кноб",
                      floor_lock=False,
                      closer=False,
                      handle_height=1000,
                      painting=False, ral_color=None, custom_colors=False):
    """
    Расчёт системы JV Line с парковкой
    """
    
    # ===== 1. ОПРЕДЕЛЕНИЕ ПАРАМЕТРОВ СИСТЕМЫ =====
    side_profiles_count = 0
    if left_edge == "боковой профиль":
        side_profiles_count += 1
    if right_edge == "боковой профиль":
        side_profiles_count += 1
    
    gap_with_profile = 20
    gap_without_profile = 10
    total_gap = side_profiles_count * gap_with_profile + (2 - side_profiles_count) * gap_without_profile
    
    joint_gap = 6
    total_joint_gap = (panels - 1) * joint_gap
    
    # ===== 2. РАСЧЁТ ШИРИНЫ СТЕКЛА =====
    standard_width = (width - total_gap - total_joint_gap) / panels
    glass_widths = [standard_width] * panels
    glass_widths = [round((gw + 0.05) // 0.1 * 0.1, 1) for gw in glass_widths]
    pivot_width = glass_widths[0]
    standard_width = glass_widths[1] if panels > 1 else glass_widths[0]
    
    glass_height = height - 150
    
    # ===== 3. РАСЧЁТ ГЛУБИНЫ ПАРКОВКИ =====
    parking_depth = 200 + 35 * panels
    parking_width = standard_width - 100
    if parking_width < 0:
        parking_width = 0
    
    # ===== 4. ПРОФИЛИ С ЗАПАСОМ НА РЕЗКУ =====
    ln010_length = width - 200 + parking_width - 78 + parking_depth + 44
    ln010_cut_waste = 75 + 5 * 0
    ln010_total = ln010_length + ln010_cut_waste
    
    ln020_lengths = []
    for i, gw in enumerate(glass_widths):
        if i == 0 or i == panels - 1:
            ln020_lengths.append(gw - 15 - 3)
        else:
            ln020_lengths.append(gw + 6)
    
    ln020_total_length = sum(ln020_lengths)
    ln020_cuts = panels - 1
    ln020_cut_waste = 75 + 5 * ln020_cuts
    ln020_total = ln020_total_length + ln020_cut_waste
    ln030_total = ln020_total
    
    ln040_length = height - 58
    ln040_cut_waste = 75 + 5 * 1
    ln040_total_per_piece = ln040_length + ln040_cut_waste
    ln040_qty = 2
    
    # ===== 5. КОМПЛЕКТУЮЩИЕ =====
    ln050_code = "LN-050-L" if opening == "влево" else "LN-050-R"
    ln050_qty = 1
    
    rollers_qty = panels - 1 if panels > 1 else 0
    
    ln080_qty = 0
    if panels >= 1:
        ln080_qty += 1
    if panels >= 2:
        ln080_qty += 1
    if panels >= 3:
        ln080_qty += 1
    
    ln090_qty = 0
    if panels >= 2:
        ln090_qty += 1
    if panels > 3:
        ln090_qty += (panels - 3)
    
    ln100_qty = ln080_qty + ln090_qty + 1
    
    ln110_qty = 1 if handle_type == "кноб" else 0
    ln120_qty = 1
    ln130_qty = 1
    
    ln150_qty = 3
    if ln010_length > 6000:
        ln150_qty += (ln010_length // 6000)
    
    ln160_qty = 1
    
    # ===== 6. ЗАГЛУШКИ =====
    joints_count = panels - 1 if panels > 1 else 0
    
    if opening == "влево":
        ln_tl_qty = joints_count * 2
        ln_tr_qty = 0
    else:
        ln_tl_qty = 0
        ln_tr_qty = joints_count * 2
    
    ln_bl_qty = ln_tl_qty
    ln_br_qty = ln_tr_qty
    
    ln_tsl_qty = 1
    ln_tsr_qty = 1
    ln_bsl_qty = 1
    ln_bsr_qty = 1
    
    # ===== 7. УПЛОТНИТЕЛИ =====
    aa010_qty = 0
    for gw in glass_widths:
        if gw < 800:
            aa010_qty += 1
        elif gw < 1600:
            aa010_qty += 2
        else:
            aa010_qty += 3
    
    aa020_length = ln010_length + 400
    aa050_qty = joints_count
    aa070_qty = 2 if panels >= 2 else 1
    aa090_qty = 1 if panels > 2 else 0
    
    # ===== 8. РАСЧЁТ КЛЕЯ И АКТИВАТОРА =====
    # Для лайна: клей наносится на 4 стороны створочника (сверху, снизу, слева, справа)
    glue_per_panel_m = (standard_width / 1000) * 4
    total_glue_length_m = glue_per_panel_m * panels
    
    glue_tubes = max(1, int((total_glue_length_m + 17.999) // 18))
    activator_bottles = glue_tubes
    
    # ===== ФОРМИРОВАНИЕ РЕЗУЛЬТАТА =====
    result = {
        "system_info": {
            "type": "JV Line",
            "opening": opening,
            "panels": panels,
            "width_mm": width,
            "height_mm": height,
            "glass_widths_mm": glass_widths,
            "glass_height_mm": glass_height,
            "parking_depth_mm": parking_depth,
            "parking_width_mm": parking_width,
            "total_gap_mm": total_gap,
            "joint_gap_mm": joint_gap,
            "pivot_width_mm": pivot_width,
            "standard_width_mm": standard_width,
            "glass_weight_kg": round((standard_width / 1000) * (glass_height / 1000) * 25, 1),
            "handle_height_mm": handle_height,
            "painting": painting,
            "ral_color": ral_color,
            "custom_colors": custom_colors
        },
        "profiles": [
            {
                "code": "LN-010",
                "name": "Профиль несущий",
                "length_per_piece_mm": ln010_length,
                "cut_waste_mm": ln010_cut_waste,
                "total_with_waste_mm": ln010_total,
                "qty": 1,
                "total_m": round(ln010_total / 1000, 3)
            },
            {
                "code": "LN-020",
                "name": "Профиль створочный верхний",
                "length_per_piece_mm": round(standard_width, 1),
                "cut_waste_mm": ln020_cut_waste,
                "total_with_waste_mm": round(ln020_total, 1),
                "qty": panels,
                "total_m": round(ln020_total / 1000, 3),
                "note": f"Резов: {ln020_cuts}, запас: {ln020_cut_waste} мм"
            },
            {
                "code": "LN-030",
                "name": "Профиль створочный нижний",
                "length_per_piece_mm": round(standard_width, 1),
                "cut_waste_mm": ln020_cut_waste,
                "total_with_waste_mm": round(ln030_total, 1),
                "qty": panels,
                "total_m": round(ln030_total / 1000, 3),
                "note": f"Резов: {ln020_cuts}, запас: {ln020_cut_waste} мм"
            },
            {
                "code": "LN-040",
                "name": "Профиль боковой",
                "length_per_piece_mm": ln040_length,
                "cut_waste_mm": ln040_cut_waste,
                "total_with_waste_mm": ln040_total_per_piece,
                "qty": ln040_qty,
                "total_m": round(ln040_total_per_piece / 1000 * ln040_qty, 3)
            }
        ],
        "hardware": [
            {
                "code": ln050_code,
                "name": "Тройник " + ("левый" if opening == "влево" else "правый"),
                "qty": ln050_qty
            },
            {
                "code": "LN-060",
                "name": "Роликовая каретка низкая",
                "qty": rollers_qty
            },
            {
                "code": "LN-070-A",
                "name": "Роликовая каретка высокая",
                "qty": rollers_qty
            },
            {
                "code": "LN-080",
                "name": "Защёлка боковая",
                "qty": ln080_qty
            },
            {
                "code": "LN-090",
                "name": "Защёлка продольная",
                "qty": ln090_qty
            },
            {
                "code": "LN-100",
                "name": "Ответная втулка защёлки",
                "qty": ln100_qty
            },
            {
                "code": "LN-110",
                "name": "Ручка-кноб",
                "qty": ln110_qty
            },
            {
                "code": "LN-120",
                "name": "Поворотный узел нижний (комплект)",
                "qty": ln120_qty
            },
            {
                "code": "LN-130",
                "name": "Поворотный узел верхний (комплект)",
                "qty": ln130_qty
            },
            {
                "code": "LN-150",
                "name": "Пластина соединительная",
                "qty": ln150_qty
            },
            {
                "code": "LN-160",
                "name": "Пластина соединительная 90°",
                "qty": ln160_qty
            },
            {
                "code": "LN-TL" if opening == "влево" else "LN-TR",
                "name": "Заглушка верхняя рядовая " + ("левая" if opening == "влево" else "правая"),
                "qty": ln_tl_qty if opening == "влево" else ln_tr_qty
            },
            {
                "code": "LN-TSL",
                "name": "Заглушка верхняя боковая левая",
                "qty": ln_tsl_qty
            },
            {
                "code": "LN-TSR",
                "name": "Заглушка верхняя боковая правая",
                "qty": ln_tsr_qty
            },
            {
                "code": "LN-BL" if opening == "влево" else "LN-BR",
                "name": "Заглушка нижняя рядовая " + ("левая" if opening == "влево" else "правая"),
                "qty": ln_bl_qty if opening == "влево" else ln_br_qty
            },
            {
                "code": "LN-BSL",
                "name": "Заглушка нижняя боковая левая",
                "qty": ln_bsl_qty
            },
            {
                "code": "LN-BSR",
                "name": "Заглушка нижняя боковая правая",
                "qty": ln_bsr_qty
            },
            {
                "code": "LN-230",
                "name": "Замок в пол (комплект)",
                "qty": 1 if floor_lock else 0
            },
            {
                "code": "LN-240",
                "name": "Башмак для напольного доводчика",
                "qty": 1 if closer else 0
            }
        ],
        "seals": [
            {
                "code": "AA-010",
                "name": "Полосовая щётка, 1,6 м",
                "qty": aa010_qty,
                "unit": "шт"
            },
            {
                "code": "AA-020",
                "name": "Уплотнитель щёточный 7х12",
                "length_mm": aa020_length,
                "total_m": round(aa020_length / 1000, 3)
            },
            {
                "code": "AA-050",
                "name": "Уплотнитель светопрозр. h-типа, 3 м",
                "qty": aa050_qty,
                "unit": "шт"
            },
            {
                "code": "AA-070",
                "name": "Уплотнитель светопрозр. D-типа, 3 м",
                "qty": aa070_qty,
                "unit": "шт"
            },
            {
                "code": "AA-090",
                "name": "Уплотнитель светопрозр. магнитн. 45°, 3 м",
                "qty": aa090_qty,
                "unit": "шт"
            }
        ],
        "consumables": [
            {
                "code": "AA-110",
                "name": "Активатор (50 мл)",
                "qty": int(activator_bottles),
                "unit": "шт"
            },
            {
                "code": "AA-120",
                "name": "Клей (уп. колбаса)",
                "qty": int(glue_tubes),
                "unit": "уп"
            }
        ],
        "fasteners": [
            {
                "code": "AA-208",
                "name": "Саморезы 3x16 гол. впотай - для заглушек",
                "qty": (ln_tl_qty + ln_tr_qty + ln_tsl_qty + ln_tsr_qty + 
                       ln_bl_qty + ln_br_qty + ln_bsl_qty + ln_bsr_qty),
                "unit": "шт"
            }
        ],
        "summary": {
            "total_profiles_m": round(
                (ln010_total + ln020_total + ln030_total + 
                 ln040_total_per_piece * ln040_qty) / 1000, 3
            ),
            "total_seals_m": round(aa020_length / 1000, 3),
            "total_hardware_items": (
                ln050_qty + rollers_qty * 2 + ln080_qty + ln090_qty + 
                ln100_qty + ln110_qty + ln120_qty + ln130_qty + ln150_qty + 
                ln160_qty + ln_tl_qty + ln_tr_qty + ln_tsl_qty + ln_tsr_qty + 
                ln_bl_qty + ln_br_qty + ln_bsl_qty + ln_bsr_qty + 
                (1 if floor_lock else 0) + (1 if closer else 0)
            ),
            "plug_distribution": (
                f"Верхние рядовые: {ln_tl_qty + ln_tr_qty}, "
                f"Верхние боковые: {ln_tsl_qty + ln_tsr_qty}, "
                f"Нижние рядовые: {ln_bl_qty + ln_br_qty}, "
                f"Нижние боковые: {ln_bsl_qty + ln_bsr_qty}"
            ),
            "glue_info": f"Клей: {int(glue_tubes)} туб, Активатор: {int(activator_bottles)} банок (на {total_glue_length_m:.1f} м шва)"
        }
    }
    
    return result


def calculate_jv_zigzag(width, height, panels,
                        opening="влево",
                        left_edge="боковой профиль",
                        right_edge="боковой профиль",
                        floor_lock=False,
                        handle_height=1000,
                        painting=False, ral_color=None, custom_colors=False,
                        glass_width_override=None):
    """
    Расчёт системы JV Zig-Zag (гармошка) для ОДНОЙ СТОРОНЫ системы
    
    Параметры:
        width: ширина проёма для расчёта зазоров (мм)
        height: высота проёма (мм)
        panels: количество створок для одной стороны (дробное: 1.5, 2.5, 3.5, 4.5)
        opening: направление открывания ("влево", "вправо")
        left_edge/right_edge: тип края ("боковой профиль", "без профиля")
        floor_lock: нужен ли замок в пол
        handle_height: высота от пола до ручки (мм)
        painting: нужна ли покраска
        ral_color: цвет по карте RAL
        custom_colors: задать цвет вручную для каждого профиля
        glass_width_override: предварительно рассчитанная ширина створки (мм) для систем с открыванием от центра
    
    Возвращает: словарь с расчётом комплектующих для одной стороны системы
    """
    
    # ===== ВАЛИДАЦИЯ =====
    if panels % 1 == 0:
        raise ValueError(f"Количество створок должно быть дробным (1.5, 2.5, 3.5, 4.5), получено: {panels}")
    if panels < 1.5 or panels > 4.5:
        raise ValueError(f"Количество створок должно быть от 1.5 до 4.5, получено: {panels}")
    
    # ===== 1. РАСЧЁТ ШИРИНЫ СТЕКЛА =====
    integer_panels = int(panels)  # целое количество полноценных створок
    
    if glass_width_override is not None:
        # Используем предварительно рассчитанную одинаковую ширину створки (для систем от центра)
        glass_width = glass_width_override
        if glass_width <= 0:
            raise ValueError(f"Некорректная ширина створки: {glass_width} мм")
    else:
        # Стандартный расчёт по формуле из ТЗ для одной стороны (открывание от края)
        # Формула: =ОКРУГЛВНИЗ((B1-((B4*15)+10+(((ЦЕЛОЕ(B3))*7)))-42)/B3)
        # где B1 = width, B4 = 1 (боковой профиль), B3 = panels
        side_profiles_count = 1
        glass_width = (width - ((side_profiles_count * 15) + 10 + (integer_panels * 7)) - 42) / panels
        glass_width = int(glass_width)  # ОКРУГЛВНИЗ
        
        if glass_width <= 0:
            raise ValueError(
                f"Невозможно рассчитать створку: ширина проёма {width} мм слишком мала "
                f"для {panels} створок. Минимальная ширина: "
                f"{((1 * 15) + 10 + (integer_panels * 7)) + 42 + panels} мм"
            )
    
    # Ширина поворотной створки = половина ширины стандартной створки
    pivot_width = glass_width / 2
    standard_width = glass_width
    
    # Высота стекла
    glass_height = height - 150
    
    # Общее количество физических створок = целое количество + 1 (половинчатая поворотная)
    total_panels = integer_panels + 1
    
    # ===== 2. ПРОВЕРКА ВЛЕЗАНИЯ СИСТЕМЫ В ПРОЁМ =====
    # Зазоры для одной стороны:
    # - слева (у стены): 15 мм (боковой профиль)
    # - между створками: 7 мм на каждый стык (всего стыков = total_panels - 1)
    # - справа (у центра или стены): 10 мм
    total_gaps = 15 + (total_panels - 1) * 7 + 10
    
    # Ширина стекол:
    # - поворотная створка: pivot_width
    # - полноценные створки: standard_width * integer_panels
    total_glass_width = pivot_width + standard_width * integer_panels
    
    # Общая ширина системы для этой стороны:
    system_width = total_gaps + total_glass_width
    
    # Проверка влезания (с допуском 2 мм на погрешность округления)
    if system_width > width + 2:
        raise ValueError(
            f"Система не влезает в проём! "
            f"Рассчитанная ширина: {system_width:.1f} мм, "
            f"ширина проёма: {width} мм. "
            f"Створка: {standard_width} мм, поворотная: {pivot_width:.1f} мм. "
            f"Попробуйте уменьшить количество створок или увеличить ширину проёма."
        )
    
    # ===== 3. ПРОФИЛИ С ЗАПАСОМ НА РЕЗКУ =====
    # Профиль несущий (LN-010)
    ln010_length = width
    ln010_cut_waste = 75 + 5 * 0
    ln010_total = ln010_length + ln010_cut_waste
    
    # Профиль створочный верхний/нижний (LN-020/LN-030)
    ln020_lengths = []
    for i in range(total_panels):
        if i == 0:  # поворотная створка (половинчатая)
            ln020_lengths.append(pivot_width - 15 - 3)
        else:  # полноценные створки
            ln020_lengths.append(standard_width + 6)
    
    ln020_total_length = sum(ln020_lengths)
    ln020_cuts = total_panels - 1
    ln020_cut_waste = 75 + 5 * ln020_cuts
    ln020_total = ln020_total_length + ln020_cut_waste
    ln030_total = ln020_total
    
    # Профиль боковой (LN-040)
    ln040_length = height - 58  # 58 мм - высота верхнего профиля
    ln040_cut_waste = 75 + 5 * 1
    ln040_total_per_piece = ln040_length + ln040_cut_waste
    ln040_qty = 1  # для одной стороны только 1 боковой профиль
    
    # ===== 4. КОМПЛЕКТУЮЩИЕ =====
    # Роликовые каретки (на все створки кроме поворотной)
    rollers_qty = total_panels - 1 if total_panels > 1 else 0
    
    # Защёлки боковые: 2 шт на последнюю створку + 1 шт на каждую центральную створку
    ln080_qty = 2
    if integer_panels > 1:  # есть центральные створки
        ln080_qty += (integer_panels - 1)
    
    # Ответные втулки: общее количество защелок + 1 запасная
    ln100_qty = ln080_qty + 1
    
    # Ручки и поворотные узлы (только на поворотную створку)
    ln110_qty = 1  # LN-110 (ручка-кноб)
    ln120_qty = 1  # LN-120 (нижний поворотный узел)
    ln130_qty = 1  # LN-130 (верхний поворотный узел)
    
    # Пластины соединительные
    ln150_qty = 1  # 1 шт на систему
    
    # ===== 5. ЗАГЛУШКИ =====
    # Количество стыков между створками
    joints_count = total_panels - 1
    
    # Боковые заглушки (по спецификации)
    total_panels_with_half = total_panels  # включая половинчатую
    
    if total_panels_with_half % 2 == 0:
        # Чётное количество: 1 левая и 1 правая заглушки
        ln_tsl_qty = 1
        ln_tsr_qty = 1
    else:
        # Нечётное количество
        if opening == "влево":
            ln_tsl_qty = 0
            ln_tsr_qty = 2
        else:  # вправо
            ln_tsl_qty = 2
            ln_tsr_qty = 0
    
    # Нижние боковые заглушки (аналогично верхним)
    ln_bsl_qty = ln_tsl_qty
    ln_bsr_qty = ln_tsr_qty
    
    # ===== 6. ПЕТЛИ =====
    ln210_qty = joints_count  # Верхние петли
    ln220_qty = joints_count  # Нижние петли
    
    # ===== 7. УПЛОТНИТЕЛИ =====
    # AA-010: полосовая щётка (1.6 м = 1600 мм, вставляется в 2 паза на створку)
    aa010_qty = 0
    brush_length_mm = 1600
    for i in range(total_panels):
        gw = pivot_width if i == 0 else standard_width
        total_brush_length_mm = gw * 2  # два паза на створку
        # Округление вверх: (длина + 1599) // 1600
        brushes_needed = (total_brush_length_mm + brush_length_mm - 1) // brush_length_mm
        aa010_qty += brushes_needed
    
    # AA-020: уплотнитель щёточный 7х12 (длина несущего профиля × 2)
    aa020_length = ln010_length * 2
    
    # AA-050: уплотнитель светопрозр. h-типа (по 1 шт на каждый стык)
    aa050_qty = joints_count
    
    # AA-070: уплотнитель светопрозр. D-типа (на крайних створках)
    aa070_qty = 2 if total_panels >= 2 else 1
    
    # ===== 8. РАСЧЁТ КЛЕЯ И АКТИВАТОРА =====
    # Для зиг-зага: клей наносится на 4 стороны створочника (сверху, снизу, слева, справа)
    glue_per_panel_m = (standard_width / 1000) * 4
    total_glue_length_m = glue_per_panel_m * total_panels
    
    # 1 туба клея + 1 банка активатора хватает на 18 метров клеевого шва
    glue_tubes = max(1, int((total_glue_length_m + 17.999) // 18))  # округление вверх
    activator_bottles = glue_tubes
    
    # ===== 9. КРЕПЁЖ =====
    total_plugs = ln_tsl_qty + ln_tsr_qty + ln_bsl_qty + ln_bsr_qty
    ln208_qty = total_plugs  # Саморезы для заглушек (по 1 шт на заглушку)
    ln209_qty = (ln210_qty + ln220_qty) * 2  # Саморезы для петель (по 2 шт на петлю)
    
    # ===== 10. РАСЧЁТ МАССЫ СТВОРКИ =====
    glass_area = (standard_width / 1000) * (glass_height / 1000)
    glass_weight_kg = glass_area * 25  # 10мм закалённое стекло ≈ 25 кг/м²
    
    # ===== ФОРМИРОВАНИЕ РЕЗУЛЬТАТА =====
    result = {
        "system_info": {
            "type": "JV Zig-Zag",
            "opening": opening,
            "panels": panels,
            "width_mm": width,
            "height_mm": height,
            "glass_width_mm": standard_width,
            "glass_height_mm": glass_height,
            "pivot_width_mm": pivot_width,
            "integer_panels": integer_panels,
            "has_half_panel": True,
            "total_physical_panels": total_panels,
            "glass_weight_kg": round(glass_weight_kg, 1),
            "handle_height_mm": handle_height,
            "painting": painting,
            "ral_color": ral_color,
            "custom_colors": custom_colors,
            "system_width_check_mm": system_width,
            "glass_width_source": "precalculated" if glass_width_override else "calculated"
        },
        "profiles": [
            {
                "code": "LN-010",
                "name": "Профиль несущий",
                "length_per_piece_mm": ln010_length,
                "cut_waste_mm": ln010_cut_waste,
                "total_with_waste_mm": ln010_total,
                "qty": 1,
                "total_m": round(ln010_total / 1000, 3)
            },
            {
                "code": "LN-020",
                "name": "Профиль створочный верхний",
                "length_per_piece_mm": round(standard_width, 1),
                "cut_waste_mm": ln020_cut_waste,
                "total_with_waste_mm": round(ln020_total, 1),
                "qty": total_panels,
                "total_m": round(ln020_total / 1000, 3),
                "note": f"Резов: {ln020_cuts}, запас: {ln020_cut_waste} мм"
            },
            {
                "code": "LN-030",
                "name": "Профиль створочный нижний",
                "length_per_piece_mm": round(standard_width, 1),
                "cut_waste_mm": ln020_cut_waste,
                "total_with_waste_mm": round(ln030_total, 1),
                "qty": total_panels,
                "total_m": round(ln030_total / 1000, 3),
                "note": f"Резов: {ln020_cuts}, запас: {ln020_cut_waste} мм"
            },
            {
                "code": "LN-040",
                "name": "Профиль боковой",
                "length_per_piece_mm": ln040_length,
                "cut_waste_mm": ln040_cut_waste,
                "total_with_waste_mm": ln040_total_per_piece,
                "qty": ln040_qty,
                "total_m": round(ln040_total_per_piece / 1000 * ln040_qty, 3)
            }
        ],
        "hardware": [
            {
                "code": "LN-070-A",
                "name": "Роликовая каретка высокая",
                "qty": rollers_qty
            },
            {
                "code": "LN-080",
                "name": "Защёлка боковая",
                "qty": ln080_qty
            },
            {
                "code": "LN-100",
                "name": "Ответная втулка защёлки",
                "qty": ln100_qty
            },
            {
                "code": "LN-110",
                "name": "Ручка-кноб",
                "qty": ln110_qty
            },
            {
                "code": "LN-120",
                "name": "Поворотный узел нижний (комплект)",
                "qty": ln120_qty
            },
            {
                "code": "LN-130",
                "name": "Поворотный узел верхний (комплект)",
                "qty": ln130_qty
            },
            {
                "code": "LN-150",
                "name": "Пластина соединительная",
                "qty": ln150_qty
            },
            {
                "code": "LN-TSL",
                "name": "Заглушка верхняя боковая левая",
                "qty": ln_tsl_qty
            },
            {
                "code": "LN-TSR",
                "name": "Заглушка верхняя боковая правая",
                "qty": ln_tsr_qty
            },
            {
                "code": "LN-BSL",
                "name": "Заглушка нижняя боковая левая",
                "qty": ln_bsl_qty
            },
            {
                "code": "LN-BSR",
                "name": "Заглушка нижняя боковая правая",
                "qty": ln_bsr_qty
            },
            {
                "code": "LN-210",
                "name": "Верхняя петля для гармошки (комплект)",
                "qty": ln210_qty
            },
            {
                "code": "LN-220",
                "name": "Нижняя петля для гармошки (комплект)",
                "qty": ln220_qty
            },
            {
                "code": "LN-230",
                "name": "Замок в пол (комплект)",
                "qty": 1 if floor_lock else 0
            }
        ],
        "seals": [
            {
                "code": "AA-010",
                "name": "Полосовая щётка, 1,6 м",
                "qty": aa010_qty,
                "unit": "шт"
            },
            {
                "code": "AA-020",
                "name": "Уплотнитель щёточный 7х12",
                "length_mm": aa020_length,
                "total_m": round(aa020_length / 1000, 3)
            },
            {
                "code": "AA-050",
                "name": "Уплотнитель светопрозр. h-типа, 3 м",
                "qty": aa050_qty,
                "unit": "шт"
            },
            {
                "code": "AA-070",
                "name": "Уплотнитель светопрозр. D-типа, 3 м",
                "qty": aa070_qty,
                "unit": "шт"
            }
        ],
        "consumables": [
            {
                "code": "AA-110",
                "name": "Активатор (50 мл)",
                "qty": int(activator_bottles),
                "unit": "шт"
            },
            {
                "code": "AA-120",
                "name": "Клей (уп. колбаса)",
                "qty": int(glue_tubes),
                "unit": "уп"
            }
        ],
        "fasteners": [
            {
                "code": "AA-208",
                "name": "Саморезы 3x16 гол. впотай - для заглушек",
                "qty": ln208_qty,
                "unit": "шт"
            },
            {
                "code": "AA-209",
                "name": "Саморезы 5,5x19 гол. впотай - для петель",
                "qty": ln209_qty,
                "unit": "шт"
            }
        ],
        "summary": {
            "total_profiles_m": round(
                (ln010_total + ln020_total + ln030_total + 
                 ln040_total_per_piece * ln040_qty) / 1000, 3
            ),
            "total_seals_m": round(aa020_length / 1000, 3),
            "total_hardware_items": (
                rollers_qty + ln080_qty + ln100_qty + ln110_qty + 
                ln120_qty + ln130_qty + ln150_qty + 
                ln_tsl_qty + ln_tsr_qty + ln_bsl_qty + ln_bsr_qty + 
                ln210_qty + ln220_qty + (1 if floor_lock else 0)
            ),
            "plug_distribution": (
                f"Верхние боковые: {ln_tsl_qty + ln_tsr_qty}, "
                f"Нижние боковые: {ln_bsl_qty + ln_bsr_qty}, "
                f"Всего: {total_plugs} шт"
            ),
            "glue_info": f"Клей: {int(glue_tubes)} туб, Активатор: {int(activator_bottles)} банок (на {total_glue_length_m:.1f} м шва)",
            "physical_panels": total_panels,
            "width_validation": f"Система влезает: {system_width:.1f} мм ≤ {width} мм"
        }
    }
    
    return result