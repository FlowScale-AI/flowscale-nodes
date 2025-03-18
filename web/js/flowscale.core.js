import { app } from '../../../scripts/app.js'
import { api } from '../../../scripts/api.js'

// Load the Flowscale CSS
const link = document.createElement('link');
link.rel = 'stylesheet';
link.type = 'text/css';
link.href = 'extensions/flowscale-nodes/web/css/emoji.css';
document.head.appendChild(link);

// Add HTML title renderer
const origDrawNodeTitle = app.Canvas.prototype.drawNodeTitle;
app.Canvas.prototype.drawNodeTitle = function(ctx, node, title) {
    // Check if it's a Flowscale node
    if (title && title.includes('flowscale-icon')) {
        const temp = document.createElement('div');
        temp.innerHTML = title;
        const plainTitle = temp.textContent || temp.innerText;
        
        // Draw icon first
        const icon = document.createElement('span');
        icon.className = 'flowscale-icon';
        const iconWidth = 16;
        const iconHeight = 23;
        
        // Draw the plain text title
        ctx.save();
        ctx.fillStyle = node.constructor.title_color || "#fff";
        ctx.font = node.constructor.title_text_font || "bold 14px Arial";
        ctx.textAlign = "center";
        
        // Add padding for the icon
        const titleX = node.size[0] * 0.5;
        const titleY = -node.size[1] * 0.1;
        ctx.fillText(plainTitle, titleX + iconWidth/2, titleY);
        ctx.restore();
        
        // Now we need to create a temporary canvas to draw the icon
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = iconWidth;
        tempCanvas.height = iconHeight;
        const tempCtx = tempCanvas.getContext('2d');
        
        // Create image from the SVG data URL in the CSS
        const img = new Image();
        img.src = 'data:image/svg+xml,%3Csvg width="16" height="23" viewBox="0 0 16 23" fill="none" xmlns="http://www.w3.org/2000/svg"%3E%3Cmask id="a" maskUnits="userSpaceOnUse" x="0" y="0" width="16" height="23"%3E%3Cpath d="M15.387 0H0v23h15.387V0z" fill="%23fff"/%3E%3C/mask%3E%3Cg mask="url(%23a)"%3E%3Cpath d="M7.973 0a3.25 3.25 0 00-3.248 3.243v1.474H3.25A3.25 3.25 0 000 7.962v3.242h4.724v2.947H3.248a3.25 3.25 0 00-3.25 3.244V23h3.252a3.25 3.25 0 003.245-3.244h.004v-2.141l-.009.001V3.975l.007.002v-.733a1.224 1.224 0 011.227-1.477h5.643v1.477c-.001.391-.157.765-.434 1.041-.277.277-.652.432-1.043.432H7.166v1.769h4.973a3.25 3.25 0 003.248-3.243V0H7.973zm-3.248 9.436H1.772V7.962c0-.391.157-.766.433-1.044a1.48 1.48 0 011.045-.434h1.475v2.952zm0 10.32c0 .39-.156.765-.433 1.041a1.48 1.48 0 01-1.043.433H1.771v-3.834c0-.391.156-.766.434-1.043a1.48 1.48 0 011.044-.433h1.476v3.833zm2.441-8.551h3.727v1.475c-.001.39-.157.765-.434 1.041-.277.276-.652.431-1.043.432H7.166v1.77h2.25a3.25 3.25 0 003.249-3.244h.001v-3.244H7.166v1.77z" fill="url(%23b)"/%3E%3C/g%3E%3ClinearGradient id="b" x1="-5.671" y1="-5.671" x2="17.736" y2="10.559" gradientUnits="userSpaceOnUse"%3E%3Cstop stop-color="%231659DA"/%3E%3Cstop offset="1" stop-color="%2316CFDA"/%3E%3C/linearGradient%3E%3C/svg%3E';
        
        img.onload = function() {
            // Draw the icon to the left of the text
            ctx.drawImage(img, titleX - (node.size[0] * 0.25), titleY - iconHeight/2, iconWidth, iconHeight);
        };
        
    } else {
        // Use original drawing for non-Flowscale nodes
        origDrawNodeTitle.call(this, ctx, node, title);
    }
};

async function uploadVideo(file) {
    try {
        // Wrap file in formdata so it includes filename
        const body = new FormData();
        const new_file = new File([file], file.name, {
            type: file.type,
            lastModified: file.lastModified,
        });
        body.append("image", new_file);
        
        const resp = await api.fetchApi("/upload/image", {
            method: "POST",
            body,
        });

        if (resp.status === 200) {
            return resp;
        } else {
            alert(resp.status + " - " + resp.statusText);
        }
    } catch (error) {
        alert(error);
    }
}

async function getVideoList() {
    try {
        const res = await api.fetchApi('/fs/get_video_files');  // Fixed endpoint URL
        if (res.status === 200) {
            const data = await res.json();
            return data.files || [];
        }
        return [];
    } catch (error) {
        console.error("Error fetching video files:", error);
        return [];
    }
}

function addVideoUploadFeature(nodeType, nodeData) {
    const origOnNodeCreated = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function() {
        if (origOnNodeCreated) {
            origOnNodeCreated.apply(this, arguments);
        }

        // Add file input element for video upload
        const fileInput = document.createElement("input");
        Object.assign(fileInput, {
            type: "file",
            accept: "video/webm,video/mp4,video/x-matroska,image/gif",
            style: "display: none",
            onchange: async function() {
                if (fileInput.files.length) {
                    const file = fileInput.files[0];
                    await uploadVideo(file);
                    // Update the video list in the node
                    const videoWidget = this.widgets.find(w => w.name === "video");
                    if (videoWidget) {
                        // Refresh the widget's values
                        videoWidget.options.values = await getVideoList();
                        videoWidget.value = file.name;
                        if (videoWidget.callback) {
                            videoWidget.callback(file.name);
                        }
                    }
                }
            }.bind(this)
        });
        
        document.body.appendChild(fileInput);

        // Add upload button widget
        const uploadWidget = this.addWidget("button", "Upload Video", null, () => {
            fileInput.click();
        });
        uploadWidget.options.serialize = false;

        // Remove file input when node is removed
        const origOnRemoved = this.onRemoved;
        this.onRemoved = function() {
            fileInput.remove();
            if (origOnRemoved) {
                origOnRemoved.apply(this, arguments);
            }
        };
    };
}

// Register extension 
app.registerExtension({
    name: "FlowScale.Core",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        console.log("Registering node type:", nodeType);
        console.log("Node data:", nodeData);
        if (nodeData.name === "FSLoadVideo") {
            addVideoUploadFeature(nodeType, nodeData);
        }
    }
});