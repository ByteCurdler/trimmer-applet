const UUID = "trimmer@ILikePython256";

const LOGSTAMP = "[" + UUID + "] ";

const Applet = imports.ui.applet;
const Lang = imports.lang;
const St = imports.gi.St;
const PopupMenu = imports.ui.popupMenu;
const GLib = imports.gi.GLib;
const Gio = imports.gi.Gio;
const GUdev = imports.gi.GUdev;
const ByteArray = imports.byteArray;

const AppletDir = imports.ui.appletManager.appletMeta[UUID].path;

const TrimHelper = 'trim.py';

const Gettext = imports.gettext;

Gettext.bindtextdomain(UUID, GLib.get_home_dir() + "/.local/share/locale");

function _(str) {
  return Gettext.dgettext(UUID, str);
}

function MyApplet(metadata, orientation, panelHeight, instanceId) {
    this._init(metadata, orientation, panelHeight, instanceId);
}

const MAX_BYTES = 65536;

MyApplet.prototype = {
    __proto__: Applet.IconApplet.prototype,

    _init: function(_metadata, orientation, panelHeight, instanceId) {
        Applet.IconApplet.prototype._init.call(this, orientation, panelHeight, instanceId);

        try {
            this.set_applet_tooltip(_("Click to trim URL"));
            this.set_applet_icon_name('trimmer');
            this._snip_timeout = null;
        }
        catch (e) {
            global.logError(e);
        }
    },

    on_applet_clicked: function(_event) {
        global.log(LOGSTAMP + "Trimmer activated")
        let clipboard = St.Clipboard.get_default();
        // global.logError(clipboard.get_text((clip, text) => {
        //     global.logError(text)
        // }))
        clipboard.get_text(St.ClipboardType.CLIPBOARD, Lang.bind(this,
            function(_clipboard, text) {
                try {
                    function blink(target, icon) {
                        target.set_applet_icon_name(icon);
                        if (target._snip_timeout !== null) {
                            clearTimeout(target._snip_timeout)
                        }
                        target._snip_timeout = setTimeout(() => {
                            target.set_applet_icon_name('trimmer');
                            target._snip_timeout = setTimeout(() => {
                                target.set_applet_icon_name(icon);
                                target._snip_timeout = setTimeout(() => {
                                    target.set_applet_icon_name('trimmer');
                                    target._snip_timeout = null
                                }, 150)
                            }, 150)
                        }, 150)
                    }
                    if (!text) {
                        blink(this, 'trimmer-nochange')
                    } else {
                        this.set_applet_icon_name('trimmer-working');
                        let proc = Gio.Subprocess.new(
                            ["/usr/bin/python3", GLib.build_filenamev([AppletDir,TrimHelper]), text],
                            Gio.SubprocessFlags.STDOUT_PIPE);
                        let streamOut = proc.get_stdout_pipe();
                        streamOut.read_bytes_async(MAX_BYTES, 0, null, Lang.bind(this, function (o,o2) {
                            let data = o.read_bytes_finish(o2);
                            let clipboard = St.Clipboard.get_default();
                            let data_string = data.get_data().toString();
                            let status = data_string.split(":")[0]
                            let result = data_string.split(":").slice(1, ).join(":")
                            if (status == "fail") {
                                global.logError(LOGSTAMP + "Trimmer error:\n" + result)
                                blink(this, 'trimmer-fail')
                            } else {
                                data_string = data_string.slice(9,)
                                if (result == text) {
                                    blink(this, 'trimmer-nochange')
                                    // global.log(LOGSTAMP + "Trimmer did not change URL \"" + text + "\"")
                                } else {
                                    clipboard.set_text(St.ClipboardType.CLIPBOARD, result);
                                    blink(this, 'trimmer-success')
                                    // global.log(LOGSTAMP + "Trimmer changed \"" + text + "\" to \"" + result + "\"")
                                }
                            }
                        }));
                    }
                } catch (e) {
                    global.logError("error", e)
                    blink(this, 'trimmer-fail')
                }
            }
        ));
    }
};

function main(metadata, orientation, panelHeight, instanceId) {
    let myApplet = new MyApplet(metadata, orientation, panelHeight, instanceId);
    return myApplet;
}
