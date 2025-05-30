// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'target.model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

TargetModel _$TargetModelFromJson(Map<String, dynamic> json) => TargetModel(
      name: json['name'] as String,
      target: (json['target'] as num).toInt(),
      dexNum: json['dexNum'] as String,
      mainTarget: json['main_target'] as bool? ?? false,
    );

Map<String, dynamic> _$TargetModelToJson(TargetModel instance) =>
    <String, dynamic>{
      'name': instance.name,
      'target': instance.target,
      'dexNum': instance.dexNum,
      'main_target': instance.mainTarget,
    };
