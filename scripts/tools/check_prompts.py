import json

# 检查JSON中的prompt
with open('quick_test_result.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('JSON中保存的Prompt数量:', len(data['prompts']))
print('\n所有Prompt:')
for i, p in enumerate(data['prompts'], 1):
    print(f'\n{i}. 长度={len(p)}字符')
    print(f'   内容: {p}')

# 检查发送给API的内容
print('\n' + '='*60)
print('发送给模型的完整消息示例:')
print('='*60)

patient_content_length = len(data['patients'][0]['conversation'])
prompt_length = len(data['prompts'][0])
total_length = patient_content_length + prompt_length + 20  # 加上换行等

print(f'Prompt长度: {prompt_length} 字符')
print(f'患者问答记录长度: {patient_content_length} 字符')
print(f'总输入长度约: {total_length} 字符 (~{total_length//4} tokens)')

# 检查模型响应中记录的信息
if data['patients'][0]['prompt_results']:
    response = data['patients'][0]['prompt_results'][0]['model_responses'][0]
    print(f'\n实际发送的输入长度: {response.get("input_length", "N/A")} 字符')
    print(f'响应长度: {response.get("response_length", "N/A")} 字符')
