# 🤖 HackTools Bot - Gemini AI Powered Telegram Bot

**Gemini AI ও বিল্ট-ইন হ্যাকিং টুলস সহ শক্তিশালী টেলিগ্রাম বট।**
কোড রিভিউ, কোড জেনারেটর, পোর্ট স্ক্যানার, WHOIS, DNS, IP ইনফো, এনকোড/ডিকোড, রিভার্স শেল পেলোড — সব এক বটে!

> ⚠️ **সতর্কতা:** এই বটটি **শুধুমাত্র শিক্ষামূলক উদ্দেশ্যে** তৈরি। অনুমতি ছাড়া কোনো সিস্টেমে এই টুল ব্যবহার করা বেআইনি এবং শাস্তিযোগ্য অপরাধ। দয়া করে দায়িত্বশীলতার সাথে ব্যবহার করুন।

---

## ✨ ফিচারসমূহ

### 🧠 AI ফিচার (Google Gemini API)
| কমান্ড | বর্ণনা |
|---------|---------|
| `/start` | বট চালু ও পরিচিতি |
| `/write <অনুরোধ>` | Gemini AI দিয়ে নতুন Python কোড তৈরি |
| `/review <কোড>` | কোড রিভিউ (বাগ, সিকিউরিটি, ইম্প্রুভমেন্ট) |
| `<সরাসরি মেসেজ>` | যেকোনো টেক্সট/প্রশ্ন পাঠালে AI ভিত্তিক উত্তর |

### 🛠️ হ্যাকিং টুলস
| কমান্ড | বর্ণনা |
|---------|---------|
| `/scan <host> <start> <end>` | TCP পোর্ট স্ক্যানার |
| `/whois <domain>` | ডোমেইনের WHOIS তথ্য |
| `/dns <domain>` | DNS রেকর্ড (A, MX) |
| `/ipinfo <ip>` | IP অ্যাড্রেসের জিও-লোকেশন তথ্য |
| `/hash <text>` | হ্যাশ জেনারেটর (MD5, SHA1, SHA256) |
| `/encode <type> <text>` | এনকোড (base64, hex, url, rot13) |
| `/decode <type> <text>` | ডিকোড (base64, hex, url, rot13) |
| `/payload <os>` | রিভার্স শেল পেলোড জেনারেটর (linux/windows) |

---

## 📋 প্রয়োজনীয়তা

- **Python 3.8+**
- **Telegram Bot Token** ([BotFather](https://t.me/botfather) থেকে নিন)
- **Gemini API Key** ([Google AI Studio](https://aistudio.google.com/apikey) থেকে ফ্রিতে নিন)

---

## 🚀 ইনস্টলেশন ও ব্যবহার

### 🔹 স্টেপ ১: রিপোজিটরি ক্লোন
```bash
git clone https://github.com/shakil56167/hacktools-bot.git
cd hacktools-bot
