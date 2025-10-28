# 🚀 Complete Vercel Deployment Guide

## Step-by-Step Instructions

### **STEP 1: Create Vercel Account**
1. Open browser and go to: **https://vercel.com**
2. Click **"Sign Up"** button (top right corner)
3. Click **"Continue with GitHub"**
4. Enter your GitHub credentials if not logged in
5. Click **"Authorize Vercel"** to give Vercel access to your repositories

---

### **STEP 2: Import Your Project**
1. After logging in, you'll land on the Vercel Dashboard
2. Look for **"Add New..."** button (top right, next to your profile)
3. Click it and select **"Project"** from dropdown menu
4. You'll see a page titled "Import Git Repository"
5. Scroll through the list and find **"Sayar-212/Psy"**
6. Click the **"Import"** button next to it

---

### **STEP 3: Configure Project** 
You'll now see the "Configure Project" page. Fill it exactly as shown:

**Project Name:**
- Type: `psy` (or leave the auto-generated name)

**Framework Preset:**
- Select: **"Other"** from dropdown

**Root Directory:**
- Leave as: `./` (default - don't change)

**Build Settings:**
- Build Command: Leave **BLANK** (don't type anything)
- Output Directory: Leave **BLANK** (don't type anything)  
- Install Command: Leave as default

---

### **STEP 4: Add Environment Variables** ⚠️ **CRITICAL STEP**

Scroll down to find **"Environment Variables"** section:

1. Click to expand the section
2. You'll see three input fields: Name, Value, and Environment

**Add First Variable:**
- Name: `GROQ_API_KEY`
- Value: `your_groq_api_key_here`
- Environment: Leave all checked (Production, Preview, Development)
- Click **"Add"** button

**Add Second Variable:**
- Name: `MISTRAL_API_KEY`
- Value: `your_mistral_api_key_here`
- Environment: Leave all checked
- Click **"Add"** button

**Note:** Use your actual API keys from the `.env` file in the backend folder.

You should now see both variables listed.

---

### **STEP 5: Deploy**
1. Scroll to the bottom of the page
2. Click the big blue **"Deploy"** button
3. Wait while Vercel:
   - Clones your repository
   - Installs dependencies
   - Builds your project
   - Deploys to their CDN
4. This takes about **1-2 minutes**
5. You'll see a success screen with:
   - Confetti animation 🎉
   - Your deployment URL (e.g., `https://psy-abc123.vercel.app`)
   - Screenshot preview of your site

---

### **STEP 6: Test Your Deployment**
1. Click **"Visit"** button or copy the URL
2. Your site should open in a new tab
3. Test all features:
   - ✅ Landing page loads
   - ✅ Login works
   - ✅ Dashboard displays
   - ✅ PsyGen personality analysis works
   - ✅ PsyMood depression assessment works
   - ✅ WhatsApp chat analyzer works
   - ✅ Social media analyzer works

---

### **STEP 7: Set Up Custom Domain (Optional)**
1. Go back to Vercel Dashboard
2. Click on your **"psy"** project
3. Go to **"Settings"** tab
4. Click **"Domains"** in sidebar
5. Add your custom domain (if you have one)
6. Follow DNS configuration instructions

---

## 🔧 Troubleshooting

### **If API calls fail:**
1. Check Vercel Dashboard → Your Project → Settings → Environment Variables
2. Verify both API keys are present
3. Click **"Redeploy"** button to rebuild with new variables

### **If deployment fails:**
1. Check the build logs in Vercel
2. Look for error messages
3. Common issues:
   - Missing environment variables
   - Python version mismatch
   - Dependency installation errors

### **If pages don't load:**
1. Check browser console for errors (F12)
2. Verify all file paths are correct
3. Check Network tab for failed requests

---

## 📝 Important Notes

- ✅ All API endpoints updated to use `/api/` prefix
- ✅ Environment variables configured for security
- ✅ CORS enabled for cross-origin requests
- ✅ Static files served from root directory
- ✅ Backend runs as serverless functions

---

## 🎯 What Happens After Deployment

1. **Automatic Deployments:** Every time you push to GitHub, Vercel automatically redeploys
2. **Preview Deployments:** Pull requests get their own preview URLs
3. **Analytics:** View traffic and performance in Vercel Dashboard
4. **Logs:** Check function logs for debugging

---

## 🔗 Useful Links

- **Your GitHub Repo:** https://github.com/Sayar-212/Psy
- **Vercel Dashboard:** https://vercel.com/dashboard
- **Vercel Docs:** https://vercel.com/docs

---

## ✅ Deployment Checklist

- [ ] Vercel account created
- [ ] Project imported from GitHub
- [ ] Framework set to "Other"
- [ ] GROQ_API_KEY added
- [ ] MISTRAL_API_KEY added
- [ ] Deployment successful
- [ ] Site loads correctly
- [ ] All features tested
- [ ] Custom domain configured (optional)

---

**Your app is now live! 🎉**
