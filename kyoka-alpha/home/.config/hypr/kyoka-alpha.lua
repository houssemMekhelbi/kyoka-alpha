-- Kyoka alpha look and feel.
-- A desktop that never raises its voice: void planes, a violet aura felt more
-- than seen, bone type. Loaded after futuwwa.lua so these values win;
-- behaviour and binds stay there.
--
-- The theme's 14/6 fracture needs a per-window corner shader, which Hyprland
-- does not offer, so windows stay sharp (rounding 0) and the fracture is drawn where we draw: bar shards, alert
-- banners, the lock field. Only the focused window carries the aura (a violet
-- shadow); inactive planes cast plain black.

local C = {
    void   = "07060B",
    deep   = "0F0B18",
    violet = "7B4FD6",
    pale   = "A98BFF",
}

hl.config({
    general = {
        gaps_in     = 6,
        gaps_out    = 12,
        border_size = 1,
        col = {
            -- 1px border fading from Pale Violet to transparent along its length.
            active_border   = {
                colors = { "rgb(" .. C.pale .. ")", "rgb(" .. C.violet .. ")", "rgba(" .. C.violet .. "40)" },
                angle  = 160,
            },
            inactive_border = "rgba(" .. C.pale .. "2E)",
        },
    },

    decoration = {
        rounding = 0,

        active_opacity   = 0.90,
        inactive_opacity = 0.78,

        blur = {
            enabled           = true,
            size              = 10,
            passes            = 3,
            vibrancy          = 0.12,
            new_optimizations = true,
            popups            = true,
        },

        glow = {
            enabled = false,
        },

        -- The aura: 32px violet at 40% on the focused window, black elsewhere.
        shadow = {
            enabled        = true,
            range          = 32,
            render_power   = 3,
            offset         = { 0, 0 },
            color          = "rgba(" .. C.violet .. "66)",
            color_inactive = "rgba(00000088)",
        },
    },

    group = {
        col = {
            border_active   = "rgb(" .. C.pale .. ")",
            border_inactive = "rgba(" .. C.pale .. "2E)",
        },
    },

    misc = {
        disable_hyprland_logo    = true,
        disable_splash_rendering = true,
        background_color         = "rgb(" .. C.void .. ")",
    },
})

-- Cursor: KyokaShard (~/.local/share/icons/KyokaShard, hyprcursor + XCursor).
-- On a live theme switch restore.sh runs `hyprctl setcursor` from gsettings.txt.
hl.env("HYPRCURSOR_THEME", "KyokaShard")
hl.env("HYPRCURSOR_SIZE", "24")
hl.env("XCURSOR_THEME", "KyokaShard")
hl.env("XCURSOR_SIZE", "24")

-- A config reload resets the cursor to the default theme; set it again.
local function kyoka_cursor()
    hl.exec_cmd("hyprctl setcursor KyokaShard 24")
end
hl.on("hyprland.start", kyoka_cursor)
hl.on("config.reloaded", kyoka_cursor)

-- Launcher bind points at the Kyoka launcher; futuwwa.lua binds the Girih one.
hl.unbind("SUPER + D")
hl.bind("SUPER + D",
    hl.dsp.exec_cmd(os.getenv("HOME") .. "/.local/bin/kyoka-launcher"),
    { description = "Application launcher" })

-- Terminals draw their own 86% glass so text stays fully opaque.
hl.window_rule({
    name    = "kyoka-terminal-opaque",
    match   = { class = "^(foot|footclient|Alacritty|com.mitchellh.ghostty)$" },
    opacity = "1.0 override 1.0 override",
})

-- Glass for layer surfaces: waybar shards, alert banners, launcher, notifications.
-- ignore_alpha keeps the fully transparent cracks between shards unblurred.
hl.layer_rule({
    name         = "kyoka-bar-glass",
    match        = { namespace = "^hattin-" },
    blur         = true,
    ignore_alpha = 0.1,
})

hl.layer_rule({
    name         = "kyoka-launcher-glass",
    match        = { namespace = "^launcher$" },
    blur         = true,
    ignore_alpha = 0.1,
})

hl.layer_rule({
    name         = "kyoka-notify-glass",
    match        = { namespace = "^swaync" },
    blur         = true,
    ignore_alpha = 0.1,
})

-- Launcher: floating foot + fzf (~/.local/bin/kyoka-launcher), ~40% width.
hl.window_rule({
    name     = "kyoka-launcher",
    match    = { class = "^kyoka-launcher$" },
    float    = true,
    size     = "780 470",
    center   = true,
    pin      = true,
    opacity  = "1.0 override 1.0 override",
})

-- Taskwarrior popups from the waybar "yawm" module (~/.local/bin/kyoka-yawm).
hl.window_rule({
    name     = "kyoka-yawm",
    match    = { class = "^kyoka-yawm$" },
    float    = true,
    size     = "820 600",
    center   = true,
    pin      = true,
    opacity  = "1.0 override 1.0 override",
})

hl.window_rule({
    name     = "kyoka-yawm-add",
    match    = { class = "^kyoka-yawm-add$" },
    float    = true,
    size     = "720 240",
    center   = true,
    pin      = true,
    opacity  = "1.0 override 1.0 override",
})

local kyoka_popups = { "kyoka-launcher", "kyoka-yawm", "kyoka-yawm-add" }

-- Close every popup window except those of class `keep`.
-- hl.get_windows matches `class` exactly (no regex), so pass the plain name.
function kyoka_close_popups(keep)
    for _, class in ipairs(kyoka_popups) do
        if class ~= keep then
            for _, w in ipairs(hl.get_windows({ class = class })) do
                hl.dispatch(hl.dsp.window.close({ window = "address:" .. w.address }))
            end
        end
    end
end

function kyoka_close_launcher()
    kyoka_close_popups()
end

-- Close popups as soon as focus moves elsewhere.
hl.on("window.active", function(win)
    kyoka_close_popups(win and win.class)
end)
