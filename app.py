import streamlit as st
import numpy as np
import plotly.graph_objects as go
import sympy as sp

st.set_page_config(
    page_title="수학 그래프 계산기",
    layout="wide"
)

# =========================================================
# 심볼 정의
# =========================================================
x, y, z = sp.symbols('x y z')

SAFE_LOCALS = {

    "x": x,
    "y": y,
    "z": z,

    # 상수
    "e": sp.E,
    "E": sp.E,

    "pi": sp.pi,
    "π": sp.pi,

    # 삼각함수
    "sin": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan,

    "asin": sp.asin,
    "acos": sp.acos,
    "atan": sp.atan,

    # 로그
    "log": sp.log,
    "ln": sp.log,

    # 기타
    "sqrt": sp.sqrt,
    "abs": sp.Abs,
    "exp": sp.exp
}

# =========================================================
# 수식 변환
# =========================================================
def convert_expression(expr):

    expr = expr.replace(" ", "")

    # 수정됨:
    # ^ 입력 지원
    expr = expr.replace("^", "**")

    # 수정됨:
    # π 입력 지원
    expr = expr.replace("π", "pi")

    return expr


# =========================================================
# 수정됨:
# 끊김 / 점근선 처리 업그레이드
# 기존 diff 방식 -> slope 방식
# =========================================================
def clean_discontinuity(y_vals, x_vals):

    y_vals = np.array(
        y_vals,
        dtype=np.float64
    )

    # inf 제거
    y_vals[~np.isfinite(y_vals)] = np.nan

    # 너무 큰 값 제거
    threshold = 1e6

    y_vals[np.abs(y_vals) > threshold] = np.nan

    # 수정됨:
    # 기울기 기반 끊김 판정
    diff_y = np.abs(np.diff(y_vals))

    diff_x = np.abs(np.diff(x_vals))

    slope = diff_y / (diff_x + 1e-9)

    jump_indices = np.where(slope > 500)[0]

    for idx in jump_indices:

        y_vals[idx] = np.nan

        if idx + 1 < len(y_vals):

            y_vals[idx + 1] = np.nan

    return y_vals


# =========================================================
# 일반 2D 그래프
# =========================================================
def plot_2d(
    expr,
    color,
    x_min,
    x_max,
    sample_density
):

    expr_str = convert_expression(expr)

    # y= 형태 처리
    if "=" in expr_str:

        left, right = expr_str.split("=")

        if "y" in left:

            solved = sp.solve(

                sp.sympify(
                    left,
                    locals=SAFE_LOCALS
                )

                -

                sp.sympify(
                    right,
                    locals=SAFE_LOCALS
                ),

                y
            )

            expr_str = str(solved[0])

        else:

            expr_str = right

    parsed = sp.sympify(
        expr_str,
        locals=SAFE_LOCALS
    )

    f = sp.lambdify(
        x,
        parsed,
        "numpy"
    )

    # 수정됨:
    # 현재 화면 범위 기반 계산
    x_vals = np.linspace(
        x_min,
        x_max,
        sample_density
    )

    try:

        y_vals = f(x_vals)

        # 수정됨:
        # slope 기반 끊김 처리 적용
        y_vals = clean_discontinuity(
            y_vals,
            x_vals
        )

    except:

        y_vals = np.full_like(
            x_vals,
            np.nan
        )

    return go.Scattergl(

        x=x_vals,
        y=y_vals,

        mode='lines',

        line=dict(
            color=color,
            width=2
        ),

        name=expr,

        connectgaps=False
    )


# =========================================================
# 수정됨:
# 2D -> 3D 곡선
# Trace 반환 구조
# =========================================================
def plot_2d_as_3d(
    expr,
    color,
    x_min,
    x_max,
    sample_density
):

    expr_str = convert_expression(expr)

    if "=" in expr_str:

        left, right = expr_str.split("=")

        if "y" in left:

            solved = sp.solve(

                sp.sympify(
                    left,
                    locals=SAFE_LOCALS
                )

                -

                sp.sympify(
                    right,
                    locals=SAFE_LOCALS
                ),

                y
            )

            expr_str = str(solved[0])

        else:

            expr_str = right

    parsed = sp.sympify(
        expr_str,
        locals=SAFE_LOCALS
    )

    f = sp.lambdify(
        x,
        parsed,
        "numpy"
    )

    x_vals = np.linspace(
        x_min,
        x_max,
        sample_density
    )

    try:

        y_vals = f(x_vals)

        y_vals = clean_discontinuity(
            y_vals,
            x_vals
        )

    except:

        y_vals = np.full_like(
            x_vals,
            np.nan
        )

    # 수정됨:
    # Figure 반환 X
    # Trace 반환
    return go.Scatter3d(

        x=x_vals,

        y=y_vals,

        z=np.zeros_like(x_vals),

        mode='lines',

        line=dict(
            color=color,
            width=6
        ),

        name=expr
    )


# =========================================================
# 수정됨:
# 암시적 그래프 범위 연동
# =========================================================
def plot_implicit(
    expr,
    x_min,
    x_max
):

    expr = convert_expression(expr)

    left, right = expr.split("=")

    f_expr = (

        sp.sympify(
            left,
            locals=SAFE_LOCALS
        )

        -

        sp.sympify(
            right,
            locals=SAFE_LOCALS
        )
    )

    f = sp.lambdify(
        (x, y),
        f_expr,
        "numpy"
    )

    # 수정됨:
    # 현재 범위 기반 계산
    x_vals = np.linspace(
        x_min,
        x_max,
        500
    )

    y_vals = np.linspace(
        x_min,
        x_max,
        500
    )

    X, Y = np.meshgrid(
        x_vals,
        y_vals
    )

    try:

        Z = f(X, Y)

    except:

        Z = np.zeros_like(X)

    return go.Contour(

        x=x_vals,
        y=y_vals,
        z=Z,

        contours=dict(

            start=0,
            end=0,
            size=1,

            coloring="lines"
        ),

        line=dict(
            color="black",
            width=2
        ),

        showscale=False,

        name=expr
    )


# =========================================================
# 수정됨:
# 진짜 3D 그래프 범위 연동
# =========================================================
def plot_3d(
    expr,
    x_min,
    x_max
):

    expr = convert_expression(expr)

    if "=" in expr:

        _, right = expr.split("=")

        expr = right

    parsed = sp.sympify(
        expr,
        locals=SAFE_LOCALS
    )

    f = sp.lambdify(
        (x, y),
        parsed,
        "numpy"
    )

    # 수정됨:
    # 현재 범위 기반 계산
    x_vals = np.linspace(
        x_min,
        x_max,
        120
    )

    y_vals = np.linspace(
        x_min,
        x_max,
        120
    )

    X, Y = np.meshgrid(
        x_vals,
        y_vals
    )

    try:

        Z = f(X, Y)

        Z = np.where(
            np.isfinite(Z),
            Z,
            np.nan
        )

    except:

        Z = np.zeros_like(X)

    # 수정됨:
    # Figure 반환 X
    # Trace 반환
    return go.Surface(

        x=X,
        y=Y,
        z=Z,

        colorscale="Viridis",

        name=expr
    )


# =========================================================
# UI
# =========================================================
st.title("📈 수학 그래프 계산기")

st.sidebar.title("수식 입력")

# =========================================================
# 현재 화면 범위
# =========================================================
x_min = st.sidebar.number_input(
    "X 최소",
    value=-50.0
)

x_max = st.sidebar.number_input(
    "X 최대",
    value=50.0
)

if x_min >= x_max:

    st.error(
        "X 최소는 X 최대보다 작아야 합니다."
    )

    st.stop()

# =========================================================

view_width = abs(x_max - x_min)

sample_density = int(

    min(

        max(
            view_width * 200,
            3000
        ),

        120000
    )
)

st.sidebar.write(
    f"자동 샘플 밀도: {sample_density}"
)

# =========================================================
# 3D 보기
# =========================================================
view_3d = st.sidebar.checkbox(
    "3D 애니메이션으로 보기"
)

# =========================================================
# 수식 리스트
# =========================================================
if "expr_list" not in st.session_state:

    st.session_state.expr_list = [""]

for i in range(
    len(st.session_state.expr_list)
):

    st.session_state.expr_list[i] = st.sidebar.text_input(

        f"수식 {i+1}",

        st.session_state.expr_list[i],

        key=f"expr_{i}"
    )

if st.sidebar.button("➕ 수식 추가"):

    st.session_state.expr_list.append("")

# =========================================================
# 색상
# =========================================================
colors = [

    "red",
    "blue",
    "green",
    "orange",
    "purple",
    "yellow",
    "black"
]

fig = go.Figure()

color_index = 0

# =========================================================
# 그래프 렌더링
# =========================================================
for expr in st.session_state.expr_list:

    if expr.strip() == "":
        continue

    try:
        expr_conv = convert_expression(expr)

        # =================================================
        # 1. 진짜 3D (z= 형태)
        # =================================================
        if "z=" in expr_conv:
            trace = plot_3d(
                expr_conv,
                x_min,
                x_max
            )
            fig.add_trace(trace)

        # =================================================
        # 2. x, y가 모두 포함된 이변수 수식 처리
        # =================================================
        elif "x" in expr_conv and "y" in expr_conv:
            # 3D 보기 모드가 켜져 있을 경우 지원하지 않는 형식으로 처리
            if view_3d:
                st.warning(f"⚠️ '{expr}': 이변수 방정식(암시적 그래프)은 3D 뷰 변환을 지원하지 않는 형식입니다.")
                continue

            # 3D 뷰가 꺼져 있고 등호(=)가 있는 경우 정상적으로 2D 암시적 그래프 그리기
            elif "=" in expr_conv:
                trace = plot_implicit(
                    expr_conv,
                    x_min,
                    x_max
                )
                fig.add_trace(trace)
            
            # 등호가 없는 이변수 식의 경우 예외 처리
            else:
                raise ValueError("이변수 수식은 등호(=)가 포함된 방정식 형태여야 합니다.")

        # =================================================
        # 3. 2D -> 3D 보기 (일변수 함수)
        # =================================================
        elif view_3d:
            trace = plot_2d_as_3d(
                expr,
                colors[color_index % len(colors)],
                x_min,
                x_max,
                sample_density
            )
            fig.add_trace(trace)

        # =================================================
        # 4. 일반 2D (일변수 함수)
        # =================================================
        else:
            trace = plot_2d(
                expr,
                colors[color_index % len(colors)],
                x_min,
                x_max,
                sample_density
            )
            fig.add_trace(trace)

        color_index += 1

    except Exception as e:
        st.error(f"❌ 오류: {expr}")
        st.text(str(e))

# =========================================================
# 2D / 3D 레이아웃 분리
# =========================================================
if not view_3d:

    fig.update_layout(

        template="plotly_white",

        height=850,

        margin=dict(
            l=10,
            r=10,
            t=10,
            b=10
        ),

        dragmode="pan",

        hovermode="closest",

        xaxis=dict(

            range=[x_min, x_max],

            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='black',

            showgrid=True
        ),

        yaxis=dict(

            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='black',

            showgrid=True
        )
    )

else:

    fig.update_layout(

        scene=dict(

            # 수정됨:
            # 축 이름 정상화
            xaxis_title="x",
            yaxis_title="y",
            zaxis_title="z",

            camera=dict(

                eye=dict(
                    x=1.8,
                    y=1.8,
                    z=1.2
                )
            )
        ),

        height=850,

        margin=dict(
            l=0,
            r=0,
            t=0,
            b=0
        )
    )

# =========================================================
# 출력
# =========================================================
st.plotly_chart(
    fig,
    use_container_width=True
)
