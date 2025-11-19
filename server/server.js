const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const bodyParser = require('body-parser');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(bodyParser.json({ limit: '50mb' }));
app.use(bodyParser.urlencoded({ extended: true, limit: '50mb' }));

// MongoDB连接
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/medical_evaluation';
mongoose.connect(MONGODB_URI)
    .then(() => console.log('✅ MongoDB连接成功'))
    .catch(err => console.error('❌ MongoDB连接失败:', err));

// 数据模型

// 完成码模型
const CodeSchema = new mongoose.Schema({
    code: {
        type: String,
        required: true,
        unique: true,
        match: /^[a-z0-9]{4}$/,  // 4位小写字母或数字
        index: true
    },
    createdAt: {
        type: Date,
        default: Date.now
    },
    status: {
        type: String,
        enum: ['active', 'used', 'expired'],
        default: 'active'
    },
    usedAt: Date,
    description: String,
    batchId: String  // 批次ID，用于批量生成的码
});

const Code = mongoose.model('Code', CodeSchema);

// 评测数据模型
const EvaluationSchema = new mongoose.Schema({
    code: {
        type: String,
        required: true,
        index: true
    },
    patient: String,
    model: String,
    scores: {
        accuracy: {
            score: Number,
            max: Number,
            comment: String
        },
        completeness: {
            score: Number,
            max: Number,
            comment: String
        },
        clinical: {
            score: Number,
            max: Number,
            comment: String
        },
        structure: {
            score: Number,
            max: Number,
            comment: String
        },
        language: {
            score: Number,
            max: Number,
            comment: String
        }
    },
    total_score: Number,
    overall_comment: String,
    timestamp: {
        type: Date,
        default: Date.now
    },
    submittedAt: {
        type: Date,
        default: Date.now
    }
});

const Evaluation = mongoose.model('Evaluation', EvaluationSchema);

// API路由

// 1. 验证完成码
app.get('/api/verify-code/:code', async (req, res) => {
    try {
        const { code } = req.params;

        // 验证格式
        if (!/^[a-z0-9]{4}$/.test(code)) {
            return res.status(400).json({
                valid: false,
                message: '完成码格式错误，必须是4位小写字母或数字'
            });
        }

        const codeDoc = await Code.findOne({ code });

        if (!codeDoc) {
            return res.status(404).json({
                valid: false,
                message: '完成码不存在'
            });
        }

        if (codeDoc.status === 'expired') {
            return res.status(403).json({
                valid: false,
                message: '完成码已过期'
            });
        }

        res.json({
            valid: true,
            status: codeDoc.status,
            message: codeDoc.status === 'used' ? '该完成码已使用过，可以继续编辑' : '完成码验证成功'
        });
    } catch (error) {
        console.error('验证完成码失败:', error);
        res.status(500).json({
            valid: false,
            message: '服务器错误'
        });
    }
});

// 2. 申请完成码（用户自助申请）
app.post('/api/apply-code', async (req, res) => {
    try {
        // 生成唯一完成码
        let newCode;
        let attempts = 0;
        const maxAttempts = 10;

        while (attempts < maxAttempts) {
            newCode = generateCode();
            const existing = await Code.findOne({ code: newCode });
            if (!existing) {
                break;
            }
            attempts++;
        }

        if (attempts >= maxAttempts) {
            return res.status(500).json({
                success: false,
                message: '生成完成码失败，请稍后重试'
            });
        }

        // 创建完成码记录
        const codeDoc = new Code({
            code: newCode,
            description: '用户自助申请',
            batchId: `apply_${Date.now()}`
        });

        await codeDoc.save();

        console.log(`✅ 新申请的完成码: ${newCode}`);

        res.json({
            success: true,
            code: newCode,
            message: '完成码申请成功'
        });
    } catch (error) {
        console.error('申请完成码失败:', error);
        res.status(500).json({
            success: false,
            message: '服务器错误'
        });
    }
});

// 3. 提交评测数据
app.post('/api/submit-evaluation', async (req, res) => {
    try {
        const { code, ...evaluationData } = req.body;

        // 验证完成码
        const codeDoc = await Code.findOne({ code });
        if (!codeDoc) {
            return res.status(404).json({
                success: false,
                message: '完成码不存在'
            });
        }

        if (codeDoc.status === 'expired') {
            return res.status(403).json({
                success: false,
                message: '完成码已过期'
            });
        }

        // 保存评测数据
        const evaluation = new Evaluation({
            code,
            ...evaluationData
        });

        await evaluation.save();

        // 更新完成码状态
        if (codeDoc.status === 'active') {
            codeDoc.status = 'used';
            codeDoc.usedAt = new Date();
            await codeDoc.save();
        }

        res.json({
            success: true,
            message: '评测数据提交成功',
            evaluationId: evaluation._id
        });
    } catch (error) {
        console.error('提交评测失败:', error);
        res.status(500).json({
            success: false,
            message: '服务器错误: ' + error.message
        });
    }
});

// 3. 获取指定完成码的评测数据
app.get('/api/evaluations/:code', async (req, res) => {
    try {
        const { code } = req.params;
        const evaluations = await Evaluation.find({ code }).sort({ timestamp: -1 });

        res.json({
            success: true,
            count: evaluations.length,
            data: evaluations
        });
    } catch (error) {
        console.error('获取评测数据失败:', error);
        res.status(500).json({
            success: false,
            message: '服务器错误'
        });
    }
});

// 4. 生成完成码（批量）
app.post('/api/admin/generate-codes', async (req, res) => {
    try {
        const { count = 1, batchId, description } = req.body;

        if (count > 100) {
            return res.status(400).json({
                success: false,
                message: '单次最多生成100个完成码'
            });
        }

        const codes = [];
        const batchIdValue = batchId || `batch_${Date.now()}`;

        for (let i = 0; i < count; i++) {
            let newCode;
            let attempts = 0;

            // 生成唯一的4位码
            while (attempts < 10) {
                newCode = generateCode();
                const existing = await Code.findOne({ code: newCode });
                if (!existing) break;
                attempts++;
            }

            if (attempts >= 10) {
                return res.status(500).json({
                    success: false,
                    message: '生成唯一完成码失败，请重试'
                });
            }

            const codeDoc = new Code({
                code: newCode,
                batchId: batchIdValue,
                description
            });

            await codeDoc.save();
            codes.push(newCode);
        }

        res.json({
            success: true,
            count: codes.length,
            batchId: batchIdValue,
            codes
        });
    } catch (error) {
        console.error('生成完成码失败:', error);
        res.status(500).json({
            success: false,
            message: '服务器错误: ' + error.message
        });
    }
});

// 5. 获取所有完成码（管理面板）
app.get('/api/admin/codes', async (req, res) => {
    try {
        const { status, batchId } = req.query;
        const query = {};

        if (status) query.status = status;
        if (batchId) query.batchId = batchId;

        const codes = await Code.find(query).sort({ createdAt: -1 });

        // 为每个完成码统计评测数量
        const codesWithStats = await Promise.all(codes.map(async (code) => {
            const evaluationCount = await Evaluation.countDocuments({ code: code.code });
            return {
                ...code.toObject(),
                evaluationCount,
                completionRate: Math.round((evaluationCount / 80) * 100) // 80份评测
            };
        }));

        res.json({
            success: true,
            count: codesWithStats.length,
            data: codesWithStats
        });
    } catch (error) {
        console.error('获取完成码列表失败:', error);
        res.status(500).json({
            success: false,
            message: '服务器错误'
        });
    }
});

// 6. 获取统计数据
app.get('/api/admin/stats', async (req, res) => {
    try {
        const totalCodes = await Code.countDocuments();
        const activeCodes = await Code.countDocuments({ status: 'active' });
        const usedCodes = await Code.countDocuments({ status: 'used' });
        const expiredCodes = await Code.countDocuments({ status: 'expired' });

        const totalEvaluations = await Evaluation.countDocuments();

        // 按模型统计
        const modelStats = await Evaluation.aggregate([
            {
                $group: {
                    _id: '$model',
                    count: { $sum: 1 },
                    avgScore: { $avg: '$total_score' }
                }
            },
            { $sort: { count: -1 } }
        ]);

        // 按患者统计
        const patientStats = await Evaluation.aggregate([
            {
                $group: {
                    _id: '$patient',
                    count: { $sum: 1 }
                }
            },
            { $sort: { count: -1 } }
        ]);

        res.json({
            success: true,
            codes: {
                total: totalCodes,
                active: activeCodes,
                used: usedCodes,
                expired: expiredCodes
            },
            evaluations: {
                total: totalEvaluations,
                byModel: modelStats,
                byPatient: patientStats
            }
        });
    } catch (error) {
        console.error('获取统计数据失败:', error);
        res.status(500).json({
            success: false,
            message: '服务器错误'
        });
    }
});

// 7. 获取所有评测数据（管理面板）
app.get('/api/admin/evaluations', async (req, res) => {
    try {
        const { code, patient, model, page = 1, limit = 50 } = req.query;
        const query = {};

        if (code) query.code = code;
        if (patient) query.patient = patient;
        if (model) query.model = model;

        const total = await Evaluation.countDocuments(query);
        const evaluations = await Evaluation.find(query)
            .sort({ submittedAt: -1 })
            .skip((page - 1) * limit)
            .limit(parseInt(limit));

        res.json({
            success: true,
            total,
            page: parseInt(page),
            limit: parseInt(limit),
            data: evaluations
        });
    } catch (error) {
        console.error('获取评测数据失败:', error);
        res.status(500).json({
            success: false,
            message: '服务器错误'
        });
    }
});

// 辅助函数：生成4位随机码
function generateCode() {
    const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
    let code = '';
    for (let i = 0; i < 4; i++) {
        code += chars[Math.floor(Math.random() * chars.length)];
    }
    return code;
}

// 启动服务器
app.listen(PORT, () => {
    console.log(`🚀 服务器运行在 http://localhost:${PORT}`);
    console.log(`📊 MongoDB URI: ${MONGODB_URI}`);
});
