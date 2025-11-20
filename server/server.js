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
    patient: {
        type: String,
        required: true
    },
    model: {
        type: String,
        required: true
    },
    scores: {
        accuracy: {
            score: Number,
            max: Number,
            weight: Number,
            comment: String
        },
        completeness: {
            score: Number,
            max: Number,
            weight: Number,
            comment: String
        },
        standard: {
            score: Number,
            max: Number,
            weight: Number,
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

// 创建复合唯一索引：同一个 code + patient + model 只能有一条记录
EvaluationSchema.index({ code: 1, patient: 1, model: 1 }, { unique: true });

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

        // 保存或更新评测数据（覆盖模式）
        // 使用 code + patient + model 作为唯一标识，存在则更新，不存在则创建
        const evaluation = await Evaluation.findOneAndUpdate(
            {
                code: code,
                patient: evaluationData.patient,
                model: evaluationData.model
            },
            {
                code,
                ...evaluationData,
                submittedAt: new Date()  // 更新提交时间
            },
            {
                upsert: true,  // 不存在则创建
                new: true       // 返回更新后的文档
            }
        );

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

        // 计算平均分
        const avgScoreResult = await Evaluation.aggregate([
            {
                $group: {
                    _id: null,
                    avgScore: { $avg: '$total_score' }
                }
            }
        ]);
        const avgScore = avgScoreResult.length > 0 ? avgScoreResult[0].avgScore : 0;

        // 计算今日评测数（从今天0点开始）
        const todayStart = new Date();
        todayStart.setHours(0, 0, 0, 0);
        const todayCount = await Evaluation.countDocuments({
            submittedAt: { $gte: todayStart }
        });

        // 计算活跃模型数（有评测记录的模型数量）
        const activeModelsResult = await Evaluation.distinct('model');
        const activeModels = activeModelsResult.length;

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
                avgScore: avgScore,           // 新增：平均分
                todayCount: todayCount,       // 新增：今日评测数
                activeModels: activeModels,   // 新增：活跃模型数
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

// 8. 获取单个评测详情（根据ID）
app.get('/api/admin/evaluation/:id', async (req, res) => {
    try {
        const { id } = req.params;

        // 验证ID格式
        if (!mongoose.Types.ObjectId.isValid(id)) {
            return res.status(400).json({
                success: false,
                message: '无效的评测ID'
            });
        }

        const evaluation = await Evaluation.findById(id);

        if (!evaluation) {
            return res.status(404).json({
                success: false,
                message: '未找到该评测记录'
            });
        }

        res.json({
            success: true,
            data: evaluation
        });
    } catch (error) {
        console.error('获取评测详情失败:', error);
        res.status(500).json({
            success: false,
            message: '服务器错误: ' + error.message
        });
    }
});

// 9. 清空数据库（危险操作）
app.post('/api/admin/clear-database', async (req, res) => {
    try {
        console.log('⚠️  执行清空数据库操作...');

        // 删除所有完成码
        const deletedCodes = await Code.deleteMany({});

        // 删除所有评测记录
        const deletedEvaluations = await Evaluation.deleteMany({});

        console.log(`✅ 数据库已清空: 删除了 ${deletedCodes.deletedCount} 个完成码, ${deletedEvaluations.deletedCount} 条评测记录`);

        res.json({
            success: true,
            message: '数据库已清空',
            deletedCodes: deletedCodes.deletedCount,
            deletedEvaluations: deletedEvaluations.deletedCount
        });
    } catch (error) {
        console.error('清空数据库失败:', error);
        res.status(500).json({
            success: false,
            message: '服务器错误: ' + error.message
        });
    }
});

// 10. 获取评测矩阵数据（每个模型在每个患者的平均分和标准差）
app.get('/api/admin/evaluation-matrix', async (req, res) => {
    try {
        // 聚合统计：按模型和患者分组，计算平均分和标准差
        const matrixData = await Evaluation.aggregate([
            {
                $group: {
                    _id: {
                        model: '$model',
                        patient: '$patient'
                    },
                    avgScore: { $avg: '$total_score' },
                    stdDev: { $stdDevPop: '$total_score' },
                    count: { $sum: 1 },
                    scores: { $push: '$total_score' }
                }
            },
            {
                $sort: {
                    '_id.model': 1,
                    '_id.patient': 1
                }
            }
        ]);

        // 获取所有唯一的模型和患者列表
        const models = await Evaluation.distinct('model');
        const patients = await Evaluation.distinct('patient');

        // 转换为矩阵格式
        const matrix = {};
        matrixData.forEach(item => {
            const modelName = item._id.model;
            const patientName = item._id.patient;

            if (!matrix[modelName]) {
                matrix[modelName] = {};
            }

            matrix[modelName][patientName] = {
                avg: item.avgScore || 0,
                stdDev: item.stdDev || 0,
                count: item.count,
                scores: item.scores
            };
        });

        res.json({
            success: true,
            models: models.sort(),
            patients: patients.sort(),
            matrix: matrix
        });
    } catch (error) {
        console.error('获取评测矩阵数据失败:', error);
        res.status(500).json({
            success: false,
            message: '服务器错误: ' + error.message
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
