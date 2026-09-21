from django.utils import timezone

LAYOUT_THEMES = [
    {"key": "blue", "class": "bg-blue"},
    {"key": "azure", "class": "bg-azure"},
    {"key": "indigo", "class": "bg-indigo"},
    {"key": "purple", "class": "bg-purple"},
    {"key": "pink", "class": "bg-pink"},
    {"key": "red", "class": "bg-red"},
    {"key": "orange", "class": "bg-orange"},
    {"key": "yellow", "class": "bg-yellow"},
    {"key": "lime", "class": "bg-lime"},
    {"key": "green", "class": "bg-green"},
    {"key": "teal", "class": "bg-teal"},
    {"key": "cyan", "class": "bg-cyan"},
]

LAYOUT_FONTS = [
    {"key": "sans-serif", "label": "layout.settings.fontSansSerif"},
    {"key": "serif", "label": "layout.settings.fontSerif"},
    {"key": "monospace", "label": "layout.settings.fontMonospace"},
    {"key": "comic", "label": "layout.settings.fontComic"},
]

LAYOUT_BASES = ["slate", "gray", "zinc", "neutral", "stone"]
LAYOUT_RADII = ["0", "0.5", "1", "1.5", "2"]


def layout_context(request):
    return {
        "layout_themes": LAYOUT_THEMES,
        "layout_fonts": LAYOUT_FONTS,
        "layout_bases": LAYOUT_BASES,
        "layout_radii": LAYOUT_RADII,
    }


def user_context(request):
    return {
        "current_user": {
            "username": request.session.get("username", ""),
            "is_authenticated": bool(request.session.get("access_token")),
        }
    }


def footer_context(request):
    year = timezone.now().year
    lang = getattr(request, "LANGUAGE_CODE", "th") or "th"
    return {"display_year": year + 543 if lang.startswith("th") else year}


def menu_context(request):
    """Sidebar + header menus (static — extend from DB when ready)."""

    sidebar = [
        {"label": "nav.dashboard", "icon": "layout-dashboard", "route_name": "dashboard:index"},
        {
            "label": "nav.jobs", "icon": "briefcase",
            "children": [
                {"label": "nav.jobList", "icon": "list", "route_name": "dashboard:index"},
                {"label": "nav.jobBoard", "icon": "layers", "route_name": "dashboard:index"},
                {"label": "nav.jobCreate", "icon": "plus", "route_name": "dashboard:index"},
            ],
        },
        {
            "label": "nav.users", "icon": "users",
            "children": [
                {"label": "nav.userList", "icon": "list", "route_name": "dashboard:index"},
                {"label": "nav.roles", "icon": "shield", "route_name": "dashboard:index"},
            ],
        },
        {"label": "nav.settings", "icon": "settings", "route_name": "dashboard:index"},
    ]

    apps = [
        {"label": "layout.header.appDashboard", "icon": "layout-dashboard", "route_name": "dashboard:index"},
        {"label": "layout.header.appUsers", "icon": "users", "route_name": "dashboard:index"},
        {"label": "layout.header.appAI", "icon": "robot", "route_name": "dashboard:index"},
        {"label": "layout.header.appReports", "icon": "chart-bar", "route_name": "dashboard:index"},
        {"label": "layout.header.appLanguages", "icon": "language", "route_name": "dashboard:index"},
        {"label": "layout.header.appSettings", "icon": "settings", "route_name": "dashboard:index"},
    ]

    profile_menu = [
        {"label": "layout.header.profile", "icon": "user", "route_name": "dashboard:index"},
        {"label": "layout.header.analytics", "icon": "chart-pie", "route_name": "dashboard:index"},
        {"divider": True},
        {"label": "layout.header.settingsPrivacy", "route_name": "dashboard:index"},
        {"label": "layout.header.help", "route_name": "dashboard:index"},
        {"label": "layout.header.signOut", "action": "logout"},
    ]

    horizontal_menu = [
        {"label": "nav.dashboard", "icon": "layout-dashboard", "route_name": "dashboard:index"},
        {"label": "nav.users", "icon": "users", "route_name": "dashboard:index"},
        {"label": "nav.settings", "icon": "settings", "route_name": "dashboard:index"},
    ]

    return {
        "menu_items": sidebar,
        "app_items": apps,
        "profile_menu": profile_menu,
        "horizontal_menu": horizontal_menu,
        "notifications": [
            {"id": 1, "title": "layout.header.notifNewJob",
             "time": "layout.header.notifTime5min", "read": False},
            {"id": 2, "title": "layout.header.notifQuotationApproved",
             "time": "layout.header.notifTime1hour", "read": False},
            {"id": 3, "title": "layout.header.notifLowStock",
             "time": "layout.header.notifTime2hours", "read": True},
        ],
        "unread_count": 2,
    }
