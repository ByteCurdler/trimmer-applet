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

const TrimHelper = 'trimmer.py';

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
                        let icon;
                        if (status == "fail") {
                            icon = 'trimmer-fail'
                            global.logError(LOGSTAMP + "Trimmer error:\n" + result)
                        } else {
                            data_string = data_string.slice(9,)
                            if (result == text) {
                                icon = 'trimmer-nochange'
                                // global.log(LOGSTAMP + "Trimmer did not change URL \"" + text + "\"")
                            } else {
                                clipboard.set_text(St.ClipboardType.CLIPBOARD, result);
                                icon = 'trimmer-success'
                                // global.log(LOGSTAMP + "Trimmer changed \"" + text + "\" to \"" + result + "\"")
                            }
                        }
                        this.set_applet_icon_name(icon);
                        if (this._snip_timeout !== null) {
                            clearTimeout(this._snip_timeout)
                        }
                        this._snip_timeout = setTimeout(() => {
                            this.set_applet_icon_name('trimmer');
                            this._snip_timeout = setTimeout(() => {
                                this.set_applet_icon_name(icon);
                                this._snip_timeout = setTimeout(() => {
                                    this.set_applet_icon_name('trimmer');
                                }, 150)
                            }, 150)
                        }, 150)
                    }));
                } catch (e) {
                    global.logError("error", e)
                }
            }
        ));
    }
};

function main(metadata, orientation, panelHeight, instanceId) {
    let myApplet = new MyApplet(metadata, orientation, panelHeight, instanceId);
    return myApplet;
}
